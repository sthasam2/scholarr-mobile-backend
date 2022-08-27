from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from apps.class_groups.api.serializers import (
    ClassGroupSerializer,
    CreateClassGroupSerializer,
    CreateInviteClassGroupMemberSerializer,
    CreateRequestClassGroupMemberSerializer,
    PublicClassGroupSerializer,
    ReadClassGroupMemberSerializer,
    UpdateClassGroupSerializer,
)
from apps.class_groups.models import (
    ClassGroup,
    ClassGroupHasStudent,
    ClassGroupStudentInviteOrRequest,
)
from apps.class_groups.permissions import IsClassGroupOwner
from apps.class_groups.utils import (
    accept_class_group_invite_request,
    create_classgroup_invite,
    create_classgroup_request,
    delete_class_group_invite_request,
    get_reqbody_classgroup_or_raise,
    get_url_id_classgroup_invite_request_or_raise,
    get_url_id_classgroup_or_raise,
    reject_class_group_invite_request,
)
from apps.core.decorators import try_except_http_error_decorator
from apps.core.exceptions import (
    AlreadyMemberError,
    AlreadyRespondedError,
    PermissionDeniedError,
)
from apps.core.helpers import RequestFieldsChecker, create_200
from apps.core.permissions import IsAuthenticatedCustom
from apps.core.utils import CodeGenerator
from apps.users.api.serializers import UserSerializer

#########################
#   CLASS GROUP
#########################


class ClassGroupViewset(ModelViewSet):
    """Viewset for Classgroup"""

    queryset = ClassGroup.objects.all()
    permission_classes = [IsAuthenticatedCustom]

    serializer_class = PublicClassGroupSerializer
    creator_serializer = ClassGroupSerializer
    create_serializer = CreateClassGroupSerializer
    update_serializer = UpdateClassGroupSerializer

    def get_permissions(self):
        """Get permissions"""

        permission_classes = [IsAuthenticatedCustom]

        if self.action in [
            "update",
            "partial_update",
            "destroy",
            "set_active_inactive",
        ]:
            permission_classes.append(IsClassGroupOwner)

        return [permission() for permission in permission_classes]

    # HTTP Methods

    @try_except_http_error_decorator
    def list(self, *args, **kwargs):
        """Class group get method"""

        serializer = self.serializer_class

        class_group_instances = self.queryset
        class_group_serializer = serializer(class_group_instances, many=True)

        return Response(
            data=dict(
                class_groups=class_group_serializer.data,
                count=class_group_serializer.data.__len__(),
            ),
            status=200,
        )

    @try_except_http_error_decorator
    def list_self_classgroups(self, *args, **kwargs):
        """Class group get method"""

        serializer = self.serializer_class

        student_class_group_instances = [
            student_classgroup.classgroup
            for student_classgroup in self.request.user.student_classgroup.all()
        ]
        created_class_group_instances = self.request.user.created_classgroup.all()

        created_class_group_serializer = serializer(
            created_class_group_instances, many=True
        )
        student_class_group_serializer = serializer(
            student_class_group_instances, many=True
        )

        return Response(
            data=dict(
                student_classgroups=student_class_group_serializer.data,
                created_classgroups=created_class_group_serializer.data,
                # count=class_group_serializer.data.__len__(),
            ),
            status=200,
        )

    @try_except_http_error_decorator
    def retrieve(self, *args, **kwargs):
        """Details of a given class group"""

        url_id = kwargs.get("class_group_id", None)
        class_group_instance = get_url_id_classgroup_or_raise(id=url_id)

        serializer = self.serializer_class(class_group_instance)
        if class_group_instance._created_by == self.request.user:
            serializer = self.creator_serializer(class_group_instance)

        return Response(
            data=serializer.data,
            status=200,
        )

    @extend_schema(request=create_serializer)
    @try_except_http_error_decorator
    def post(self, *args, **kwargs):
        """Create a class group"""

        serializer = self.create_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            _created_by=self.request.user,
            classgroup_code=CodeGenerator().generate_classgroup_code(),
        )

        return Response(
            create_200(
                201,
                "Created",
                "Classgroup Created",
                dict(classgroup=serializer.data),
            ),
            status=201,
        )

    @extend_schema(request=update_serializer)
    @try_except_http_error_decorator
    def update(self, *args, **kwargs):
        """Update a class group"""

        # Get class group and check permission
        url_id = kwargs.get("class_group_id", None)
        class_group_instance = get_url_id_classgroup_or_raise(url_id)
        self.check_object_permissions(self.request, class_group_instance)

        #  Use serializer to check and update
        serializer = self.update_serializer(data=self.request.data)
        r_checker = RequestFieldsChecker()
        r_checker.check_at_least_one_field_or_raise(
            req_body=self.request.data, field_options=serializer.Meta.fields
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(class_group_instance, **serializer.validated_data)

        return Response(
            create_200(
                200,
                "Updated",
                "Classgroup Updated",
                dict(classgroup=serializer.data),
            ),
            status=200,
        )

    @extend_schema(request=update_serializer)
    @try_except_http_error_decorator
    def partial_update(self, *args, **kwargs):
        """Partial Update a class group"""

        # Get class group and check permission
        url_id = kwargs.get("class_group_id", None)
        class_group_instance = get_url_id_classgroup_or_raise(url_id)
        self.check_object_permissions(self.request, class_group_instance)

        #  Use serializer to check and update
        serializer = self.update_serializer(data=self.request.data)
        checker = RequestFieldsChecker()
        checker.check_at_least_one_field_or_raise(
            req_body=self.request.data, field_options=serializer.Meta.fields
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(class_group_instance, **serializer.validated_data)

        return Response(
            create_200(
                200,
                "Partially Updated",
                "Classgroup Partially Updated",
                dict(classgroup=serializer.data),
            ),
            status=200,
        )

    @try_except_http_error_decorator
    def destroy(self, *args, **kwargs):
        """Delete Method for Class Group"""

        url_id = kwargs.get("class_group_id", None)
        class_group_instance = get_url_id_classgroup_or_raise(url_id)
        self.check_object_permissions(self.request, class_group_instance)

        if class_group_instance is not None:
            class_group_instance.delete()

        return Response(
            create_200(
                205,
                "Deleted",
                "Class Group Deleted!",
            ),
            status=205,
        )

    @try_except_http_error_decorator
    def toggle_active(self, request, *args, **kwargs):
        """Turn a classgroup Active/ Inactive"""

        url_id = kwargs.get("class_group_id", None)
        class_group_instance = get_url_id_classgroup_or_raise(url_id)
        self.check_object_permissions(self.request, class_group_instance)

        if class_group_instance is not None:
            class_group_instance.active = not class_group_instance.active
            class_group_instance.save()

        return Response(
            create_200(
                200,
                "Class Group Updated!",
                f"Class Group active status changed to {class_group_instance.active}",
            ),
            status=200,
        )


#########################
#   MEMBERSHIP
#########################


class ClassGroupMemberViewset(ViewSet):
    """Viewset for Class Group Member Logics"""

    permission_classes = [IsAuthenticatedCustom]
    serializer_class = CreateInviteClassGroupMemberSerializer
    request_serializer = CreateRequestClassGroupMemberSerializer
    retrieve_serializer_class = ReadClassGroupMemberSerializer
    user_serializer_class = UserSerializer

    field_options = ["id", "username", "email", "classgroup_id", "classgroup_code"]

    def get_permissions(self):
        """Get permissions"""

        permission_classes = [IsAuthenticatedCustom]

        if self.action in ["create_invite"]:
            permission_classes.append(IsClassGroupOwner)

        return [permission() for permission in permission_classes]

    @try_except_http_error_decorator
    def list_invites_requests(self, *args, **kwargs):
        """Get Invite or Requests"""

        requesting_user = self.request.user

        invites_requests_queryset = requesting_user.student_inviterequest_classgroup

        invited_list = invites_requests_queryset.filter(
            Q(invited=True) & Q(accepted=False) & Q(rejected=False)
        )
        requested_list = invites_requests_queryset.filter(
            Q(requested=True) & Q(accepted=False) & Q(rejected=False)
        )
        accepted_list = invites_requests_queryset.filter(accepted=True)
        rejected_list = invites_requests_queryset.filter(rejected=True)

        invite_serializer = self.retrieve_serializer_class(invited_list, many=True)
        request_serializer = self.retrieve_serializer_class(requested_list, many=True)
        accepted_serializer = self.retrieve_serializer_class(accepted_list, many=True)
        rejected_serializer = self.retrieve_serializer_class(rejected_list, many=True)

        return Response(
            dict(
                invites=invite_serializer.data,
                requests=request_serializer.data,
                accepted=accepted_serializer.data,
                rejected=rejected_serializer.data,
            ),
            status=200,
        )

    @try_except_http_error_decorator
    def list_classgroup_invites_requests(self, *args, **kwargs):
        """Get Invite or Requests"""

        requesting_user = self.request.user
        url_classgroup_id = kwargs.get("classgroup_id", None)
        classgroup_instance = get_url_id_classgroup_or_raise(url_classgroup_id)

        invites_requests_queryset = (
            classgroup_instance.classgroup_inviterequest_student.all()
        )

        invited_list = invites_requests_queryset.filter(
            Q(invited=True) & Q(accepted=False) & Q(rejected=False)
        )
        requested_list = invites_requests_queryset.filter(
            Q(requested=True) & Q(accepted=False) & Q(rejected=False)
        )
        accepted_list = invites_requests_queryset.filter(accepted=True)
        rejected_list = invites_requests_queryset.filter(rejected=True)

        invite_serializer = self.retrieve_serializer_class(invited_list, many=True)
        request_serializer = self.retrieve_serializer_class(requested_list, many=True)
        accepted_serializer = self.retrieve_serializer_class(accepted_list, many=True)
        rejected_serializer = self.retrieve_serializer_class(rejected_list, many=True)

        return Response(
            dict(
                invites=invite_serializer.data,
                requests=request_serializer.data,
                accepted=accepted_serializer.data,
                rejected=rejected_serializer.data,
            ),
            status=200,
        )

    @try_except_http_error_decorator
    def list_classgroup_members(self, *args, **kwargs):
        """Get Members"""

        requesting_user = self.request.user
        url_classgroup_id = kwargs.get("classgroup_id", None)
        classgroup_instance = get_url_id_classgroup_or_raise(url_classgroup_id)

        member_list = [
            classgroup_student.student
            for classgroup_student in classgroup_instance.classgroup_student.all()
        ]

        member_serializer = self.user_serializer_class(member_list, many=True)

        return Response(
            dict(
                members=member_serializer.data,
            ),
            status=200,
        )

    @extend_schema(request=serializer_class)
    @try_except_http_error_decorator
    def create_invite(self, *args, **kwargs):
        """Invite a user to become a member for class"""

        # serialize req body and check validity
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        # Check req body
        r_checker = RequestFieldsChecker()
        r_checker.check_at_least_one_field_or_raise(
            self.request.data, self.field_options
        )

        classgroup_instance = get_reqbody_classgroup_or_raise(self.request)
        self.check_object_permissions(self.request, classgroup_instance)

        create_classgroup_invite(self.request, classgroup_instance)

        # TODO create notification/email

        return Response(
            create_200(
                201,
                "User Invited",
                "Successfully Invited user to join classroom",
                "ClassGroup Invite",
            ),
            status=201,
        )

    @extend_schema(request=request_serializer)
    @try_except_http_error_decorator
    def create_request(self, *args, **kwargs):
        """Request to become a member of classgroup"""

        # serialize req body and check validity
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        # Check req body
        r_checker = RequestFieldsChecker()
        r_checker.check_at_least_one_field_or_raise(
            self.request.data, self.field_options
        )

        # Get Classgroup
        classgroup_instance = get_reqbody_classgroup_or_raise(self.request)

        # create
        create_classgroup_request(self.request, classgroup_instance)

        # TODO create notification/email

        return Response(
            create_200(
                201,
                "Membership Requested",
                "Successfully requested to join classroom",
                "ClassGroup Request",
            ),
            status=201,
        )

    @try_except_http_error_decorator
    def accept_invite_or_request(self, *args, **kwargs):
        """Method for accepting invite or request"""

        url_id = kwargs.get("invite_request_id", None)
        invite_request_instance = get_url_id_classgroup_invite_request_or_raise(url_id)
        accept_class_group_invite_request(self.request, invite_request_instance)

        # TODO create email/notification

        return Response(
            create_200(
                201,
                "Membership Accepted",
                "Successfully added as a member of class-group",
                "ClassGroup Invite/Request Accept",
            ),
            status=201,
        )

    @try_except_http_error_decorator
    def reject_invite_or_request(self, *args, **kwargs):
        """Method for rejecting invite or request"""

        url_id = kwargs.get("invite_request_id", None)
        invite_request_instance = get_url_id_classgroup_invite_request_or_raise(url_id)
        reject_class_group_invite_request(self.request, invite_request_instance)

        # TODO create email/notification

        return Response(
            create_200(
                201,
                "Membership Rejected",
                "Successfully rejected for membership of class-group",
                "ClassGroup Invite/Request Reject",
            ),
            status=201,
        )

    @try_except_http_error_decorator
    def delete_invite_or_request(self, *args, **kwargs):
        """Method for rejecting invite or request"""

        url_id = kwargs.get("invite_request_id", None)
        invite_request_instance = get_url_id_classgroup_invite_request_or_raise(url_id)
        delete_class_group_invite_request(self.request, invite_request_instance)

        # TODO create email/notification

        return Response(
            create_200(
                204,
                "Invite/Request Deleted",
                "Successfully deleted request for membership of class-group",
                "ClassGroup Invite/Request Delete",
            ),
            status=204,
        )
