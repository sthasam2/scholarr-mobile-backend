from django.db.models import Q

from apps.class_groups.models import (
    ClassGroup,
    ClassGroupHasStudent,
    ClassGroupStudentInviteOrRequest,
)
from apps.core.exceptions import (
    AlreadyInvitedError,
    AlreadyMemberError,
    AlreadyRequestedError,
    AlreadyRespondedError,
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


def get_url_id_classgroup_or_raise(id=None):
    """Get class groups"""

    if id:

        try:
            return ClassGroup.objects.get(id=id)

        except (TypeError, ValueError, OverflowError, ClassGroup.DoesNotExist):
            raise NoneExistenceError(
                cause="ClassGroup",
                status_code=400,
                message="Non existence",
                verbose=f"ClassGroup(id={id}) does not exist!",
            )

    else:
        raise UrlParameterError(
            cause="ClassGroup id in URL",
            status_code=400,
            message="URL parameter wrong",
            verbose="[id] must be provided!",
        )


def get_reqbody_classgroup_or_raise(request):
    """Get class groups"""

    classgroup_code = request.data.get("classgroup_code", None)
    classgroup_id = request.data.get("classgroup_id", None)

    classgroup_instance = ClassGroup.objects.filter(
        Q(classgroup_code=classgroup_code) | Q(id=classgroup_id)
    )

    if len(classgroup_instance) == 0:
        raise NoneExistenceError(
            status_code=400,
            message="Non existence",
            verbose=f"Classgroup with given credentials does not exist!",
            cause=request,
        )
    elif len(classgroup_instance) > 1:
        raise MultipleInstancesError(
            cause="Invite Request",
            message="Multiple Instances",
            verbose="""Given data in request body resulted in Multiple instances of Classgroup. 
                        Since single Entity is only allowed, all the data provided must belong to single entity""",
            status_code=400,
        )
    else:
        return classgroup_instance[0]


def _check_classgroup_user_status(
    request=None,
    requesting_user=None,
    classgroup=None,
    target_user=None,
):
    """Check realtionship between classgroup and its invite/request attributes respective to users"""

    if target_user:
        if len(target_user) == 0:
            raise NoneExistenceError(
                status_code=400,
                message="Non existence",
                verbose=f"Account with given credentials does not exist!",
                cause="Invite/Request Classgroup",
            )

        if len(target_user) > 1:
            raise MultipleInstancesError(
                cause="Invite/Request Classgroup",
                message="Multiple Instances",
                verbose="""Given data in request body resulted in Multiple instances of users. 
                            Since single Entity is only allowed, all the data provided must belong to single entity""",
                status_code=400,
            )

    if requesting_user and classgroup:

        # Already Invited/Requested?
        if ClassGroupStudentInviteOrRequest.objects.filter(
            Q(classgroup=classgroup) & Q(student=requesting_user)
        ).exists():
            raise PreExistenceError(
                cause="Invite/Request Classgroup membership",
                message="Already Exists!",
                verbose=f"Invite/Request to requested classgroup exists! Requesting for membership is redundant hence rejected.",
                status_code=400,
            )


def _check_accept_reject_invite_request_permission(
    request, invite_request_instance
) -> bool:
    """Check permission for Invite(limited to invitee) and Requests(limited to requestee)"""

    if invite_request_instance.invited:
        return invite_request_instance.student == request.user

    elif invite_request_instance.requested:
        return invite_request_instance._created_by == request.user

    else:
        raise PermissionDeniedError(
            detail="Requesting User does not have the authority to accept invites/requests",
            code="Permission Denied!",
        )


def _check_delete_invite_request_permission(request, invite_request_instance) -> bool:
    """Check permission for Deleting Invite(limited to inviter) and Requests(limited to requester)"""

    if invite_request_instance.invited:
        return invite_request_instance._created_by == request.user

    elif invite_request_instance.requested:
        return invite_request_instance.student == request.user

    else:
        raise PermissionDeniedError(
            detail="Requesting User does not have the authority to accept invites/requests",
            code="Permission Denied!",
        )


def _check_classgroup_accepted_rejected(request, invite_request_instance):
    """Check whether the invite/request is already accepted or rejected"""

    if invite_request_instance.accepted or invite_request_instance.rejected:
        raise AlreadyRespondedError(
            cause="Accept Classgroup membership",
            message="Already Exists!",
            verbose="Already responded to class group! Since already either accepted or rejected for membership, it is redundant hence rejected.",
            status_code=400,
        )


def create_classgroup_request(request, classgroup):
    """"""

    requesting_user = request.user

    _check_classgroup_user_status(request, requesting_user, classgroup)

    ClassGroupStudentInviteOrRequest.objects.create(
        created_by=requesting_user,
        classgroup=classgroup,
        student=requesting_user,
        invited=False,
        requested=True,
    )


def create_classgroup_invite(request, classgroup):
    """"""

    requesting_user = request.user

    id = request.data.get("id", None)
    username = request.data.get("username", None)
    email = request.data.get("email", None)

    try:
        target_user = CustomUser.objects.filter(
            Q(id=id) | Q(username=username) | Q(email=email)
        )
        if len(target_user) == 0:
            raise CustomUser.DoesNotExist

    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        raise NoneExistenceError(
            cause="User",
            status_code=400,
            message="Non existence",
            verbose=f"User(id={id}) does not exist!",
        )

    _check_classgroup_user_status(request, requesting_user, classgroup, target_user)

    new_invite = ClassGroupStudentInviteOrRequest.objects.create(
        created_by=requesting_user,
        classgroup=classgroup,
        student=target_user.first(),
    )
    return new_invite


def get_url_id_classgroup_invite_request_or_raise(id=None):
    """Get class invite or request"""

    if id:

        try:
            return ClassGroupStudentInviteOrRequest.objects.get(id=id)

        except (
            TypeError,
            ValueError,
            OverflowError,
            ClassGroupStudentInviteOrRequest.DoesNotExist,
        ):
            raise NoneExistenceError(
                cause="ClassGroupMemberInviteOrRequest",
                status_code=400,
                message="Non existence",
                verbose=f"ClassGroup(id={id}) does not exist!",
            )

    else:
        raise UrlParameterError(
            cause="Invite/Request id in URL",
            status_code=400,
            message="URL parameter wrong",
            verbose="[invite_request_id] must be provided!",
        )


def accept_class_group_invite_request(request, invite_request_instance):
    """"""

    # Invite logic performed by target student
    _check_classgroup_accepted_rejected(request, invite_request_instance)

    permission = _check_accept_reject_invite_request_permission(
        request, invite_request_instance
    )

    if permission:
        ClassGroupHasStudent.objects.create(
            classgroup=invite_request_instance.classgroup,
            student=invite_request_instance.student,
        )

        invite_request_instance.accepted = True
        invite_request_instance.rejected = False
        invite_request_instance.save()


def reject_class_group_invite_request(request, invite_request_instance):
    """"""

    permission = _check_accept_reject_invite_request_permission(
        request, invite_request_instance
    )

    if permission:
        invite_request_instance.accepted = False
        invite_request_instance.rejected = True
        invite_request_instance.save()


def delete_class_group_invite_request(request, invite_request_instance):
    """"""

    permission = _check_delete_invite_request_permission(
        request, invite_request_instance
    )

    if permission:
        invite_request_instance.delete()
