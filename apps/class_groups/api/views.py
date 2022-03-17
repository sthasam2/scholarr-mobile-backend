from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.class_groups.api.serializers import (
    ClassGroupSerializer,
    CreateClassGroupSerializer,
    PublicClassGroupSerializer,
    UpdateClassGroupSerializer,
)
from apps.class_groups.models import ClassGroup
from apps.class_groups.permissions import IsClassGroupOwner
from apps.class_groups.utils import get_url_id_classgroup_or_raise
from apps.core.decorators import try_except_http_error_decorator
from apps.core.helpers import RequestFieldsChecker, create_200
from apps.core.permissions import IsAuthenticatedCustom
from apps.core.utils import CodeGenerator


class ClassGroupViewset(ModelViewSet):
    """Viewset for Classgroup"""

    queryset = ClassGroup.objects.all()
    permission_classes = [IsAuthenticatedCustom]

    serializer = PublicClassGroupSerializer
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

        serializer = self.serializer

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
    def retrieve(self, *args, **kwargs):
        """Details of a given class group"""

        url_id = kwargs.get("class_group_id", None)
        class_group_instance = get_url_id_classgroup_or_raise(id=url_id)

        serializer = self.serializer(class_group_instance)
        if class_group_instance._created_by == self.request.user:
            serializer = self.creator_serializer(class_group_instance)

        return Response(
            data=serializer.data,
            status=200,
        )

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
    def set_active_inactive(self, request, *args, **kwargs):
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
