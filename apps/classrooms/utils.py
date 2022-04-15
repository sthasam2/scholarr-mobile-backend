from django.db.models import Q

from apps.class_groups.models import ClassGroup
from apps.classrooms.models import (
    Classroom,
    ClassroomHasStudent,
    ClassroomHasTeacher,
    ClassroomInviteOrRequest,
)
from apps.core.exceptions import (
    AlreadyMemberError,
    AlreadyRespondedError,
    AlreadyTeacherError,
    MultipleInstancesError,
    NoneExistenceError,
    PermissionDeniedError,
    PreExistenceError,
    UrlParameterError,
)
from apps.users.models import CustomUser

#########################
#       Model Methods
#########################


def get_url_id_classroom_or_raise(id=None):
    """Get classrooms from url id"""

    if id:

        try:
            return Classroom.objects.get(id=id)

        except (TypeError, ValueError, OverflowError, Classroom.DoesNotExist):
            raise NoneExistenceError(
                cause="Classroom",
                status_code=400,
                message="Non existence",
                verbose=f"Classroom(id={id}) does not exist!",
            )

    else:
        raise UrlParameterError(
            cause="Classroom id in URL",
            status_code=400,
            message="URL parameter wrong",
            verbose="[id] must be provided!",
        )


def get_reqbody_classroom_or_raise(request):
    """Get classrooms from request body"""

    classroom_code = request.data.get("classroom_code", None)
    classroom_id = request.data.get("classroom_id", None)

    classroom_instance = Classroom.objects.filter(
        Q(classroom_code=classroom_code) | Q(id=classroom_id)
    )

    if len(classroom_instance) == 0:
        raise NoneExistenceError(
            status_code=400,
            message="Non existence",
            verbose=f"Classroom with given credentials does not exist!",
            cause="Invite Request",
        )

    elif len(classroom_instance) > 1:
        raise MultipleInstancesError(
            cause="Invite Request",
            message="Multiple Instances",
            verbose="""Given data in request body resulted in Multiple instances of Classroom. 
                        Since single Entity is only allowed, all the data provided must belong to single entity""",
            status_code=400,
        )

    else:
        return classroom_instance.first()


def get_url_id_classroom_invite_request_or_raise(id=None):
    """Get classroom invite or request"""

    if id:

        try:
            return ClassroomInviteOrRequest.objects.get(id=id)

        except (
            TypeError,
            ValueError,
            OverflowError,
            ClassroomInviteOrRequest.DoesNotExist,
        ):
            raise NoneExistenceError(
                cause="ClassroomMemberInviteOrRequest",
                status_code=400,
                message="Non existence",
                verbose=f"Classroom(id={id}) does not exist!",
            )

    else:
        raise UrlParameterError(
            cause="Invite/Request id in URL",
            status_code=400,
            message="URL parameter wrong",
            verbose="[invite_request_id] must be provided!",
        )


#########################
#   CLASSROOM INV/REQ
#########################


def _check_classroom_user_classgroup_status(
    request=None,
    requesting_user=None,
    classroom=None,
    target_user=None,
    target_classgroup=None,
):
    """Check relationship between classroom and its invite/request attributes respective to users"""

    if target_user:
        if len(target_user) == 0:
            raise NoneExistenceError(
                status_code=400,
                message="Non existence",
                verbose=f"Account with given credentials does not exist!",
                cause="Invite/Request Classroom",
            )

        if len(target_user) > 1:
            raise MultipleInstancesError(
                cause="Invite/Request Classroom",
                message="Multiple Instances",
                verbose="""Given data in request body resulted in Multiple instances of users. 
                            Since single Entity is only allowed, all the data provided must belong to single entity""",
                status_code=400,
            )

    if requesting_user and classroom:

        # Already Invited/Requested?
        if ClassroomInviteOrRequest.objects.filter(
            Q(classroom=classroom)
            & (Q(student=requesting_user) | Q(teacher=requesting_user))
        ).exists():
            raise PreExistenceError(
                cause="Invite/Request Classroom membership",
                message="Already Exists!",
                verbose=f"Invite/Request to requested classroom exists! Requesting for membership is redundant hence rejected.",
                status_code=400,
            )

    if target_classgroup:
        if len(target_classgroup) == 0:
            raise NoneExistenceError(
                status_code=400,
                message="Non existence",
                verbose=f"Classgroup with given credentials does not exist!",
                cause="Invite Request",
            )

        if len(target_classgroup) > 1:
            raise MultipleInstancesError(
                cause="Invite Request",
                message="Multiple Instances",
                verbose="""Given data in request body resulted in Multiple instances of Classgroup. 
                            Since single Entity is only allowed, all the data provided must belong to single entity""",
                status_code=400,
            )

    if target_classgroup and classroom:

        # Already Invited/Requested?
        if ClassroomInviteOrRequest.objects.filter(
            Q(classroom=classroom) & (Q(classgroup=target_classgroup.first()))
        ).exists():
            raise PreExistenceError(
                cause="Request Classroom membership",
                message="Already Exists!",
                verbose="Invite/Request to requested classroom exists! Requesting for membership is redundant hence rejected.",
                status_code=400,
            )


def _check_accept_reject_invite_request_permission(
    request, invite_request_instance
) -> bool:
    """Check permission for Invite(limited to invitee) and Requests(limited to requester)"""

    if invite_request_instance.invited:
        if invite_request_instance.student:
            return invite_request_instance.student == request.user

        if invite_request_instance.teacher:
            return invite_request_instance.teacher == request.user

        if invite_request_instance.classgroup:
            return invite_request_instance.classgroup._created_by == request.user

    elif invite_request_instance.requested:
        if invite_request_instance.classroom:
            return (
                invite_request_instance.classroom._created_by == request.user
                or request.user
                in invite_request_instance.classroom.classroom_teacher.all()
            )

    else:
        raise PermissionDeniedError(
            detail="Requesting User does not have the authority to accept invites/requests",
            code="Permission Denied!",
        )


def _check_delete_invite_request_permission(request, invite_request_instance) -> bool:
    """Check permission for Deleting Invite(limited to inviter) and Requests(limited to requester)"""

    if invite_request_instance.invited:
        if invite_request_instance.classroom:
            return (
                invite_request_instance.classroom._created_by == request.user
                or request.user
                in invite_request_instance.classroom.classroom_teacher.all()
            )

    elif invite_request_instance.requested:
        if invite_request_instance.classgroup:
            return invite_request_instance.classgroup._created_by == request.user

        return invite_request_instance._created_by == request.user

    else:
        raise PermissionDeniedError(
            detail="Requesting User does not have the authority to accept invites/requests",
            code="Permission Denied!",
        )


def _check_accepted_rejected(request, invite_request_instance):
    """Check whether the invite/request is already accepted or rejected"""

    if invite_request_instance.accepted or invite_request_instance.rejected:
        raise AlreadyRespondedError(
            cause="Accept Classroom membership",
            message="Already Exists!",
            verbose="Already responded to class group! Since already either accepted or rejected for membership, it is redundant hence rejected.",
            status_code=400,
        )


def create_classroom_request(request, classroom, target_type, classgroup=None):
    """"""

    requesting_user = request.user

    _check_classroom_user_classgroup_status(
        request=request,
        requesting_user=requesting_user,
        classroom=classroom,
        classgroup=classgroup,
    )

    if target_type == "S":
        new_request = ClassroomInviteOrRequest.objects.create(
            _created_by=requesting_user,
            classroom=classroom,
            student=requesting_user,
            invited=False,
            requested=True,
        )

    if target_type == "T":
        new_request = ClassroomInviteOrRequest.objects.create(
            _created_by=requesting_user,
            classroom=classroom,
            teacher=requesting_user,
            invited=False,
            requested=True,
        )

    if target_type == "C":
        new_request = ClassroomInviteOrRequest.objects.create(
            _created_by=requesting_user,
            classroom=classroom,
            classgroup=classgroup,
            invited=False,
            requested=True,
        )

    return new_request


def create_classroom_invite(request, classroom, target_type):
    """Invite Users to Classroom as Student(S) or Teacher(T)"""

    requesting_user = request.user

    target_user = CustomUser.objects.filter(
        Q(id=request.data.get("id", None))
        | Q(username=request.data.get("username", None))
        | Q(email=request.data.get("email", None))
    )

    target_classgroup = ClassGroup.objects.filter(
        Q(id=request.data.get("classgroup_id", None))
        | Q(classgroup_code=request.data.get("classgroup_code", None))
    )

    _check_classroom_user_classgroup_status(
        request=request,
        requesting_user=requesting_user,
        classroom=classroom,
        target_user=target_user,
        target_classgroup=target_classgroup,
    )

    if target_type == "S":
        new_invite = ClassroomInviteOrRequest.objects.create(
            _created_by=requesting_user,
            classroom=classroom,
            student=target_user.first(),
            target_type=target_type,
        )

    elif target_type == "T":
        new_invite = ClassroomInviteOrRequest.objects.create(
            _created_by=requesting_user,
            classroom=classroom,
            teacher=target_user.first(),
            target_type=target_type,
        )

    elif target_type == "C":
        new_invite = ClassroomInviteOrRequest.objects.create(
            _created_by=requesting_user,
            classroom=classroom,
            classgroup=target_classgroup.first(),
            target_type=target_type,
        )

    return new_invite


def accept_classroom_invite_request(request, invite_request_instance):
    """Accept Classroom Invite/Request"""

    _check_accepted_rejected(request, invite_request_instance)
    permission = _check_accept_reject_invite_request_permission(
        request, invite_request_instance
    )

    if permission:
        if invite_request_instance.target_type == "S":
            ClassroomHasStudent.objects.create(
                classroom=invite_request_instance.classroom,
                student=invite_request_instance.student,
            )

        elif invite_request_instance.target_type == "T":
            ClassroomHasTeacher.objects.create(
                classroom=invite_request_instance.classroom,
                teacher=invite_request_instance.teacher,
            )

        elif invite_request_instance.target_type == "C":
            target_classgroup = invite_request_instance.classgroup
            classgroup_members = [
                entry.student for entry in target_classgroup.classgroup_student.all()
            ]

            for student in classgroup_members:
                ClassroomHasStudent.objects.create(
                    classroom=invite_request_instance.classroom,
                    student=student,
                )

        invite_request_instance.accepted = True
        invite_request_instance.rejected = False
        invite_request_instance.save()

    else:
        raise PermissionDeniedError(
            detail="Requesting User does not have the authority to accept invites/requests",
            code="Permission Denied!",
        )


def reject_classroom_invite_request(request, invite_request_instance):
    """Reject Classroom Invite/Request"""

    _check_accepted_rejected(request, invite_request_instance)
    permission = _check_accept_reject_invite_request_permission(
        request, invite_request_instance
    )

    if permission:
        invite_request_instance.accepted = False
        invite_request_instance.rejected = True
        invite_request_instance.save()

    else:
        raise PermissionDeniedError(
            detail="Requesting User does not have the authority to accept invites/requests",
            code="Permission Denied!",
        )


def delete_classroom_invite_request(request, invite_request_instance):
    """Delete Classroom Invite/Request"""

    permission = _check_delete_invite_request_permission(
        request, invite_request_instance
    )

    if permission:
        invite_request_instance.delete()


#########################
#   CLASSGROUP
#########################


# def _check_classroom_classgroup_status(request, classroom, target_classgroup):
#     """Check realtionship between classroom and its invite/request attributes respective to users"""

#     if target_classgroup:
#         if len(target_classgroup) == 0:
#             raise NoneExistenceError(
#                 status_code=400,
#                 message="Non existence",
#                 verbose=f"Classgroup with given credentials does not exist!",
#                 cause="Invite Request",
#             )

#         if len(target_classgroup) > 1:
#             raise MultipleInstancesError(
#                 cause="Invite Request",
#                 message="Multiple Instances",
#                 verbose="""Given data in request body resulted in Multiple instances of Classgroup.
#                             Since single Entity is only allowed, all the data provided must belong to single entity""",
#                 status_code=400,
#             )

#     if target_classgroup and classroom:

#         # Already Invited/Requested?
#         if ClassroomInviteOrRequest.objects.filter(
#             Q(classroom=classroom) & (Q(classgroup=target_classgroup.first()))
#         ).exists():
#             raise PreExistenceError(
#                 cause="Request Classroom membership",
#                 message="Already Exists!",
#                 verbose="Invite/Request to requested classroom exists! Requesting for membership is redundant hence rejected.",
#                 status_code=400,
#             )


# def _check_accept_reject_classgroup_invite_request_permission(
#     request, invite_request_instance
# ):
#     """"""

#     if invite_request_instance.invited:
#         return invite_request_instance.classgroup._created_by == request.user

#     elif invite_request_instance.requested:
#         return (
#             invite_request_instance.classroom._created_by == request.user
#             or request.user in invite_request_instance.classroom.classroom_teacher
#         )

#     else:
#         raise PermissionDeniedError(
#             detail="Requesting User does not have the authority to accept invites/requests",
#             code="Permission Denied!",
#         )


# def _check_delete_classgroup_invite_request_permission(
#     request, invite_request_instance
# ):
#     """"""

#     if invite_request_instance.invited:
#         return (
#             invite_request_instance.classroom._created_by == request.user
#             or request.user in invite_request_instance.classroom.classroom_teacher
#         )

#     elif invite_request_instance.requested:
#         return invite_request_instance.classgroup._created_by == request.user

#     else:
#         raise PermissionDeniedError(
#             detail="Requesting User does not have the authority to accept invites/requests",
#             code="Permission Denied!",
#         )


# def _check_classgroup_accepted_rejected(request, invite_request_instance):
#     """Check whether the invite/request is already accepted or rejected"""

#     if invite_request_instance.accepted or invite_request_instance.rejected:
#         raise AlreadyRespondedError(
#             cause="Accept Classroom membership",
#             message="Already Exists!",
#             verbose="Already responded to class group! Since already either accepted or rejected for membership, it is redundant hence rejected.",
#             status_code=400,
#         )


# def create_classroom_classgroup_request(request, classroom, classgroup):
#     """"""

#     requesting_user = request.user

#     _check_classroom_classgroup_status(request, classroom, classgroup)

#     new_request = ClassroomInviteOrRequest.objects.create(
#         _created_by=requesting_user,
#         classroom=classroom,
#         classgroup=classgroup,
#         target_type="C",
#         invited=False,
#         requested=True,
#     )

#     return new_request


# def create_classroom_classgroup_invite(request, classroom):
#     """"""

#     requesting_user = request.user

#     id = request.data.get("id", None)
#     code = request.data.get("code", None)

#     target_classgroup = ClassGroup.objects.filter(Q(id=id) | Q(code=code))

#     _check_classroom_classgroup_status(request, classroom, target_classgroup)

#     new_invite = ClassroomInviteOrRequest.objects.create(
#         _created_by=requesting_user,
#         classroom=classroom,
#         classgroup=target_classgroup.first(),
#         target_type="C",
#     )

#     return new_invite


# def accept_classroom_classgroupr_invite_request(request, invite_request_instance):
#     """Accept Classroom Invite/Request"""

#     _check_accepted_rejected(request, invite_request_instance)

#     permission = _check_accept_reject_classgroup_invite_request_permission(
#         request, invite_request_instance
#     )

#     if permission:
#         target_classgroup = invite_request_instance.classgroup
#         classgroup_members = [
#             entry.student for entry in target_classgroup.classgroup_student.all()
#         ]

#         for student in classgroup_members:
#             ClassroomHasStudent.objects.create(
#                 classroom=invite_request_instance.classroom,
#                 student=student,
#             )

#         invite_request_instance.accepted = True
#         invite_request_instance.rejected = False
#         invite_request_instance.save()


# def reject_classroom_classgroup_invite_request(request, invite_request_instance):
#     """Reject Classroom Invite/Request"""

#     _check_accepted_rejected(request, invite_request_instance)

#     permission = _check_accept_reject_classgroup_invite_request_permission(
#         request, invite_request_instance
#     )

#     if permission:
#         invite_request_instance.accepted = False
#         invite_request_instance.rejected = True
#         invite_request_instance.save()


# def delete_classroom_classgroup_invite_request(request, invite_request_instance):
#     """Delete Classroom Invite/Request"""

#     permission = _check_delete_classgroup_invite_request_permission(
#         request, invite_request_instance
#     )

#     if permission:
#         invite_request_instance.delete()
