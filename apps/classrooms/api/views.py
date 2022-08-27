from django.db.models import Q
from drf_spectacular.utils import extend_schema
from requests import request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.classrooms.api.serializers import (
    ClassroomSerializer,
    CreateClassroomSerializer,
    CreateInviteClassroomMemberSerializer,
    CreateRequestClassroomMemberSerializer,
    PublicClassroomSerializer,
    ReadClassroomMemberSerializer,
    UpdateClassroomSerializer,
)
from apps.classrooms.models import (
    Classroom,
    ClassroomHasStudent,
    ClassroomHasTeacher,
    ClassroomInviteOrRequest,
)
from apps.classrooms.permissions import (
    IsClassroomInviteCreatorOrTarget,
    IsClassroomMember,
    IsClassroomOwner,
    IsClassroomOwnerOrTeacher,
)
from apps.classrooms.utils import (
    accept_classroom_invite_request,
    create_classroom_invite,
    create_classroom_request,
    delete_classroom_invite_request,
    get_reqbody_classroom_or_raise,
    get_url_id_classroom_invite_request_or_raise,
    get_url_id_classroom_or_raise,
    reject_classroom_invite_request,
)
from apps.core.decorators import try_except_http_error_decorator
from apps.core.helpers import RequestFieldsChecker, create_200
from apps.core.permissions import IsAuthenticatedCustom
from apps.core.utils import CodeGenerator
from apps.users.api.serializers import UserSerializer
from apps.users.models import CustomUser

#########################
#   CLASSROOM
#########################


class ClassroomViewset(ModelViewSet):
    """Viewset for Classroom"""

    queryset = Classroom.objects.all()
    permission_classes = [IsAuthenticatedCustom]

    serializer_class = PublicClassroomSerializer
    creator_serializer = ClassroomSerializer
    create_serializer = CreateClassroomSerializer
    update_serializer = UpdateClassroomSerializer

    def get_permissions(self):
        """Get permissions"""

        permission_classes = [IsAuthenticatedCustom]

        if self.action in [
            "update",
            "partial_update",
            "destroy",
            "toggle_archived",
        ]:
            permission_classes.append(IsClassroomOwner)

        return [permission() for permission in permission_classes]

    # HTTP Methods

    @try_except_http_error_decorator
    def list(self, *args, **kwargs):
        """Class group get method"""

        serializer = self.serializer_class

        classroom_instances = Classroom.objects.all()
        classroom_serializer = serializer(classroom_instances, many=True)

        return Response(
            data=dict(
                classrooms=classroom_serializer.data,
                count=len(classroom_serializer.data),
            ),
            status=200,
        )

    @try_except_http_error_decorator
    def list_self_classrooms(self, *args, **kwargs):
        """Class group get method"""

        serializer = self.serializer_class

        studying_classroom_instances = [
            classroom_has_student.classroom
            for classroom_has_student in self.request.user.student_classroom.all()
        ]
        teaching_classroom_instances = [
            classroom_has_teacher.classroom
            for classroom_has_teacher in self.request.user.teacher_classroom.all()
        ]

        studying_classroom_serializer = serializer(
            studying_classroom_instances, many=True
        )
        teaching_classroom_serializer = serializer(
            teaching_classroom_instances, many=True
        )

        return Response(
            data=dict(
                teaching_classrooms=teaching_classroom_serializer.data,
                studying_classrooms=studying_classroom_serializer.data,
            ),
            status=200,
        )

    @try_except_http_error_decorator
    def retrieve(self, *args, **kwargs):
        """Details of a given classroom"""

        url_id = kwargs.get("classroom_id", None)
        classroom_instance = get_url_id_classroom_or_raise(id=url_id)

        serializer = self.serializer_class(classroom_instance)
        if classroom_instance._created_by == self.request.user:
            serializer = self.creator_serializer(classroom_instance)

        return Response(
            data=serializer.data,
            status=200,
        )

    @extend_schema(request=create_serializer)
    @try_except_http_error_decorator
    def create(self, *args, **kwargs):
        """Create a classroom"""

        serializer = self.create_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        classroom_instance = serializer.save(
            _created_by=self.request.user,
            classroom_code=CodeGenerator().generate_classroom_code(),
        )

        ClassroomHasTeacher.objects.create(
            classroom=classroom_instance, teacher=self.request.user
        )

        return Response(
            create_200(
                201,
                "Created",
                "Classroom Created",
                dict(classroom=serializer.data),
            ),
            status=201,
        )

    @extend_schema(request=update_serializer)
    @try_except_http_error_decorator
    def update(self, *args, **kwargs):
        """Update a classroom"""

        # Get classroom and check permission
        url_id = kwargs.get("classroom_id", None)
        classroom_instance = get_url_id_classroom_or_raise(url_id)
        self.check_object_permissions(self.request, classroom_instance)

        #  Use serializer to check and update
        serializer = self.update_serializer(data=self.request.data)
        r_checker = RequestFieldsChecker()
        r_checker.check_at_least_one_field_or_raise(
            req_body=self.request.data, field_options=serializer.Meta.fields
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(classroom_instance, **serializer.validated_data)

        return Response(
            create_200(
                200,
                "Updated",
                "Classroom Updated",
                dict(classroom=serializer.data),
            ),
            status=200,
        )

    @try_except_http_error_decorator
    def destroy(self, *args, **kwargs):
        """Delete Method for Classroom"""

        url_id = kwargs.get("classroom_id", None)
        classroom_instance = get_url_id_classroom_or_raise(url_id)
        self.check_object_permissions(self.request, classroom_instance)

        if classroom_instance is not None:
            classroom_instance.delete()

        return Response(
            create_200(
                204,
                "Deleted",
                "Classroom Deleted!",
            ),
            status=204,
        )

    @try_except_http_error_decorator
    def toggle_archive(self, request, *args, **kwargs):
        """Archive/Unarchive a classroom"""

        url_id = kwargs.get("classroom_id", None)
        classroom_instance = get_url_id_classroom_or_raise(url_id)
        self.check_object_permissions(self.request, classroom_instance)

        if classroom_instance is not None:
            classroom_instance.archive = not classroom_instance.archive
            classroom_instance.save()

        return Response(
            create_200(
                200,
                "Classroom Updated!",
                f"Classroom archive status changed to {classroom_instance.archive}",
            ),
            status=200,
        )


class ClassroomUserViewSet(ModelViewSet):
    """View sets for Classroom"""

    queryset = ClassroomInviteOrRequest.objects.all()
    serializer_class = ReadClassroomMemberSerializer
    invite_serializer_class = CreateInviteClassroomMemberSerializer
    request_serializer_class = CreateRequestClassroomMemberSerializer
    retrieve_serializer_class = ReadClassroomMemberSerializer
    user_serializer_class = UserSerializer

    field_options = [
        "id",
        "username",
        "email",
        "classgroom_id",
        "classroom_code",
        "target_type",
    ]

    def get_permissions(self):
        """"""
        permission_classes = [IsAuthenticatedCustom]

        if self.action in ["create_invite", "list_classroom_invites_requests"]:
            permission_classes.append(IsClassroomOwnerOrTeacher)

        if self.action in ["list_classroom_members"]:
            permission_classes.append(IsClassroomMember)

        if self.action in ["get_invite_request-detail"]:
            permission_classes.append(IsClassroomInviteCreatorOrTarget)

        return [permission() for permission in permission_classes]

    @try_except_http_error_decorator
    def detail_invite_request(self, *args, **kwargs):
        """Get Details of Invite or Request"""

        invite_request_id = kwargs.get("invite_request_id", None)
        # request_id = kwargs.get("request_id", None)

        if invite_request_id:
            invite_request_instance = ClassroomInviteOrRequest.objects.get(
                id=invite_request_id
            )
            self.check_object_permissions(self.request, invite_request_instance)
            serializer = self.retrieve_serializer_class(invite_request_instance)

            return Response(
                data=serializer.data,
                status=200,
            )

        # if request_id:
        #     request_instance = ClassroomInviteOrRequest.objects.get(id=request_id)
        #     self.check_object_permissions(self.request, request_instance)
        #     serializer = self.retrieve_serializer_class(request_instance)

        #     return Response(
        #         data=serializer.data,
        #         status=200,
        #     )

    @try_except_http_error_decorator
    def list_invites_requests(self, *args, **kwargs):
        """Get Invite or Requests"""

        requesting_user = self.request.user
        # target_type = self.kwargs.get("target_type", None)

        # if target_type and target_type.upper() == "S":

        # Query
        student_ir_queryset = requesting_user.student_inviterequest_classroom.all()

        #  Filter
        student_invited_list = student_ir_queryset.filter(
            Q(invited=True) & Q(accepted=False) & Q(rejected=False)
        )
        student_requested_list = student_ir_queryset.filter(
            Q(requested=True) & Q(accepted=False) & Q(rejected=False)
        )
        student_accepted_list = student_ir_queryset.filter(accepted=True)
        student_rejected_list = student_ir_queryset.filter(rejected=True)

        # Serializer
        student_invite_serializer = self.retrieve_serializer_class(
            student_invited_list, many=True
        )
        student_request_serializer = self.retrieve_serializer_class(
            student_requested_list, many=True
        )
        student_accepted_serializer = self.retrieve_serializer_class(
            student_accepted_list, many=True
        )
        student_rejected_serializer = self.retrieve_serializer_class(
            student_rejected_list, many=True
        )

        # return Response(
        #     dict(
        # student=dict(
        #     invites=student_invite_serializer.data,
        #     requests=student_request_serializer.data,
        #     accepted=student_accepted_serializer.data,
        #     rejected=student_rejected_serializer.data,
        # ),
        #     ),
        #     status=200,
        # )

        # if target_type and target_type.upper() == "T":
        teacher_ir_queryset = requesting_user.teacher_inviterequest_classroom.all()

        teacher_invited_list = teacher_ir_queryset.filter(
            Q(invited=True) & Q(accepted=False) & Q(rejected=False)
        )
        teacher_requested_list = teacher_ir_queryset.filter(
            Q(requested=True) & Q(accepted=False) & Q(rejected=False)
        )
        teacher_accepted_list = teacher_ir_queryset.filter(accepted=True)
        teacher_rejected_list = teacher_ir_queryset.filter(rejected=True)

        teacher_invite_serializer = self.retrieve_serializer_class(
            teacher_invited_list, many=True
        )
        teacher_request_serializer = self.retrieve_serializer_class(
            teacher_requested_list, many=True
        )
        teacher_accepted_serializer = self.retrieve_serializer_class(
            teacher_accepted_list, many=True
        )
        teacher_rejected_serializer = self.retrieve_serializer_class(
            teacher_rejected_list, many=True
        )

        # return Response(
        #     dict(
        #         teacher=dict(
        #             invites=teacher_invite_serializer.data,
        #             requests=teacher_request_serializer.data,
        #             accepted=teacher_accepted_serializer.data,
        #             rejected=teacher_rejected_serializer.data,
        #         ),
        #     ),
        #     status=200,
        # )

        # if target_type and target_type.upper() == "C":
        classgroup_ir_queryset = requesting_user.created_classroom_inviterequest

        classgroup_invited_list = classgroup_ir_queryset.filter(
            Q(invited=True) & Q(accepted=False) & Q(rejected=False)
        )
        classgroup_requested_list = classgroup_ir_queryset.filter(
            Q(requested=True) & Q(accepted=False) & Q(rejected=False)
        )
        classgroup_accepted_list = classgroup_ir_queryset.filter(accepted=True)
        classgroup_rejected_list = classgroup_ir_queryset.filter(rejected=True)

        classgroup_invite_serializer = self.retrieve_serializer_class(
            classgroup_invited_list, many=True
        )
        classgroup_request_serializer = self.retrieve_serializer_class(
            classgroup_requested_list, many=True
        )
        classgroup_accepted_serializer = self.retrieve_serializer_class(
            classgroup_accepted_list, many=True
        )
        classgroup_rejected_serializer = self.retrieve_serializer_class(
            classgroup_rejected_list, many=True
        )

        # return Response(
        #     dict(
        #         classgroup=dict(
        #             invites=classgroup_invite_serializer.data,
        #             requests=classgroup_request_serializer.data,
        #             accepted=classgroup_accepted_serializer.data,
        #             rejected=classgroup_rejected_serializer.data,
        #         ),
        #     ),
        #     status=200,
        # )

        return Response(
            dict(
                student=dict(
                    invites=student_invite_serializer.data,
                    requests=student_request_serializer.data,
                    accepted=student_accepted_serializer.data,
                    rejected=student_rejected_serializer.data,
                ),
                teacher=dict(
                    invites=teacher_invite_serializer.data,
                    requests=teacher_request_serializer.data,
                    accepted=teacher_accepted_serializer.data,
                    rejected=teacher_rejected_serializer.data,
                ),
                classgroup=dict(
                    invites=classgroup_invite_serializer.data,
                    requests=classgroup_request_serializer.data,
                    accepted=classgroup_accepted_serializer.data,
                    rejected=classgroup_rejected_serializer.data,
                ),
            ),
            status=200,
        )

    @try_except_http_error_decorator
    def list_classroom_members(self, *args, **kwargs):
        """List classroom members"""

        url_classroom_id = self.kwargs.get("classroom_id", None)
        classroom_instance = get_url_id_classroom_or_raise(url_classroom_id)
        self.check_object_permissions(self.request, classroom_instance)

        student_list = [
            relation.student
            for relation in ClassroomHasStudent.objects.filter(
                classroom=url_classroom_id
            )
        ]
        teacher_list = [
            relation.teacher
            for relation in ClassroomHasTeacher.objects.filter(
                classroom=url_classroom_id
            )
        ]

        student_serializer = self.user_serializer_class(student_list, many=True)
        teacher_serializer = self.user_serializer_class(teacher_list, many=True)

        return Response(
            dict(
                student=student_serializer.data,
                teacher=teacher_serializer.data,
            ),
            status=200,
        )

    @try_except_http_error_decorator
    def list_classroom_invites_requests(self, *args, **kwargs):
        """Get Invite or Requests"""

        url_classroom_id = self.kwargs.get("classroom_id", None)
        classroom_instance = get_url_id_classroom_or_raise(url_classroom_id)
        self.check_object_permissions(self.request, classroom_instance)

        invite_request_list = ClassroomInviteOrRequest.objects.filter(
            classroom=url_classroom_id
        )

        student_requests = invite_request_list.filter(
            Q(target_type="S") & Q(requested=True)
        )
        student_invites = invite_request_list.filter(
            Q(target_type="S") & Q(invited=True)
        )

        teacher_requests = invite_request_list.filter(
            Q(target_type="T") & Q(requested=True)
        )
        teacher_invites = invite_request_list.filter(
            Q(target_type="T") & Q(invited=True)
        )

        classgroup_requests = invite_request_list.filter(
            Q(target_type="C") & Q(requested=True)
        )
        classgroup_invites = invite_request_list.filter(
            Q(target_type="C") & Q(invited=True)
        )

        student_requests_serializer = self.retrieve_serializer_class(
            student_requests, many=True
        )
        student_invites_serializer = self.retrieve_serializer_class(
            student_invites, many=True
        )

        teacher_requests_serializer = self.retrieve_serializer_class(
            teacher_requests, many=True
        )
        teacher_invites_serializer = self.retrieve_serializer_class(
            teacher_invites, many=True
        )

        classgroup_requests_serializer = self.retrieve_serializer_class(
            classgroup_requests, many=True
        )
        classgroup_invites_serializer = self.retrieve_serializer_class(
            classgroup_invites, many=True
        )

        return Response(
            dict(
                student=dict(
                    invites=student_invites_serializer.data,
                    requests=student_requests_serializer.data,
                ),
                teacher=dict(
                    invites=teacher_invites_serializer.data,
                    requests=teacher_requests_serializer.data,
                ),
                classgroup=dict(
                    invites=classgroup_invites_serializer.data,
                    requests=classgroup_requests_serializer.data,
                ),
            ),
            status=200,
        )

    @extend_schema(
        request=invite_serializer_class,
    )
    @try_except_http_error_decorator
    def create_invite(self, *args, **kwargs):
        """Invite a user to become a member for class"""

        # serialize req body and check validity
        serializer = self.invite_serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        # Check req body
        RequestFieldsChecker().check_at_least_one_field_or_raise(
            self.request.data, self.field_options
        )

        classroom_instance = get_reqbody_classroom_or_raise(self.request)
        self.check_object_permissions(self.request, classroom_instance)

        target_type = self.request.data.get("target_type")

        create_classroom_invite(self.request, classroom_instance, target_type)

        # TODO create notification/email

        return Response(
            create_200(
                201,
                "Invited",
                f"Successfully Invited user/classgroup to join classroom as {target_type}",
                "Classroom Invite",
            ),
            status=201,
        )

    @extend_schema(
        request=request_serializer_class,
    )
    @try_except_http_error_decorator
    def create_request(self, *args, **kwargs):
        """Request to become a member of classroom"""

        # serialize req body and check validity
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        # Check req body
        RequestFieldsChecker().check_at_least_one_field_or_raise(
            self.request.data, self.field_options
        )

        # Get Classgroup
        classroom_instance = get_reqbody_classroom_or_raise(self.request)

        # create
        target_type = self.request.data.get("target_type")

        create_classroom_request(self.request, classroom_instance, target_type)

        # TODO create notification/email

        return Response(
            create_200(
                201,
                "Membership Requested",
                f"Successfully requested to join classroom as {target_type}",
                "Classroom Request",
            ),
            status=201,
        )

    @try_except_http_error_decorator
    def accept_invite_or_request(self, *args, **kwargs):
        """Method for accepting invite or request"""

        url_id = kwargs.get("invite_request_id", None)
        invite_request_instance = get_url_id_classroom_invite_request_or_raise(url_id)
        accept_classroom_invite_request(self.request, invite_request_instance)

        # TODO create email/notification

        return Response(
            create_200(
                201,
                "Membership Accepted",
                "Successfully added as a member of class-group",
                "Classroom Invite/Request Accept",
            ),
            status=201,
        )

    @try_except_http_error_decorator
    def reject_invite_or_request(self, *args, **kwargs):
        """Method for rejecting invite or request"""

        url_id = kwargs.get("invite_request_id", None)
        invite_request_instance = get_url_id_classroom_invite_request_or_raise(url_id)
        reject_classroom_invite_request(self.request, invite_request_instance)

        # TODO create email/notification

        return Response(
            create_200(
                201,
                "Membership Rejected",
                "Successfully rejected for membership of class-group",
                "Classroom Invite/Request Reject",
            ),
            status=201,
        )

    @try_except_http_error_decorator
    def delete_invite_or_request(self, *args, **kwargs):
        """Method for rejecting invite or request"""

        url_id = kwargs.get("invite_request_id", None)
        invite_request_instance = get_url_id_classroom_invite_request_or_raise(url_id)
        delete_classroom_invite_request(self.request, invite_request_instance)

        # TODO create email/notification

        return Response(
            create_200(
                201,
                "Invite/Request Deleted",
                "Successfully deleted request for membership of class-group",
                "Classroom Invite/Request Delete",
            ),
            status=201,
        )
