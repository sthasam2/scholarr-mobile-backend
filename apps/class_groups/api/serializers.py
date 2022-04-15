from rest_framework import serializers

from apps.class_groups.models import ClassGroup, ClassGroupStudentInviteOrRequest
from apps.core.decorators import try_except_http_error_decorator
from apps.core.exceptions import UnknownModelFieldsError

#########################
#   CLASS GROUP
#########################


class ClassGroupSerializer(serializers.ModelSerializer):
    """Serializer for Class Group"""

    class Meta:
        model = ClassGroup
        fields = "__all__"


class PublicClassGroupSerializer(serializers.ModelSerializer):
    """Serializer for Class Group"""

    class Meta:
        model = ClassGroup
        fields = (
            "name",
            "faculty",
            "batch",
            "organisation",
            "id",
            "_created_date",
            "active",
        )


class CreateClassGroupSerializer(serializers.ModelSerializer):
    """Serializer for Creating Class Group"""

    name = serializers.CharField(
        max_length=200,
        required=True,
        help_text="Name for the class group",
    )
    faculty = serializers.CharField(
        max_length=200,
        required=True,
        help_text="Name of faculty. E.g. Computer, Management, etc.",
    )
    batch = serializers.CharField(
        max_length=200,
        required=True,
        help_text="Name of batch. E.g. CE2018, CS2019.",
    )
    organisation = serializers.CharField(
        max_length=200,
        required=True,
        help_text="Name of oraganiztion. E.g. ABC Universiy, etc.",
    )

    class Meta:
        model = ClassGroup
        fields = (
            "name",
            "faculty",
            "batch",
            "organisation",
        )


class UpdateClassGroupSerializer(serializers.ModelSerializer):
    """Serializer for Updating Class Group"""

    name = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Name for the class group",
    )
    faculty = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Name of faculty. E.g. Computer, Management, etc.",
    )
    batch = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Name of batch. E.g. CE2018, CS2019.",
    )
    organisation = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Name of oraganiztion. E.g. ABC Universiy, etc.",
    )

    class Meta:
        model = ClassGroup
        fields = (
            "name",
            "faculty",
            "batch",
            "organisation",
        )

    @try_except_http_error_decorator
    def update(self, instance, **validated_data):
        """ """
        try:
            for key, value in validated_data.items():
                if instance.__dict__.__contains__(key):
                    if instance.__getattribute__(key) != value:
                        instance.__setattr__(key, value)
                else:
                    raise UnknownModelFieldsError(
                        key,
                        f"'{instance.__class__.__name__}' object has no model field called {key}",
                    )

            instance.save()

        except UnknownModelFieldsError as error:
            print(error)
            raise error

        except Exception as error:
            print("ERROR @update\n", error)
            raise error


#########################
#   MEMBERSHIP
#########################


class CreateInviteClassGroupMemberSerializer(serializers.Serializer):
    """"""

    id = serializers.IntegerField(
        required=False,
        help_text="Id of User to Invite",
    )
    email = serializers.EmailField(
        required=False,
        help_text="Email of User to Invite",
    )
    username = serializers.CharField(
        required=False,
        help_text="Username of User to Invite",
    )
    classgroup_id = serializers.IntegerField(
        required=False,
        help_text="Id of Classgroup to Invite to",
    )
    classgroup_code = serializers.CharField(
        required=False,
        help_text="Code of Classgroup to Invite to",
    )


class CreateRequestClassGroupMemberSerializer(serializers.Serializer):
    """"""

    classgroup_id = serializers.IntegerField(
        required=False,
        help_text="Id of Classgroup to Request membership for",
    )
    classgroup_code = serializers.CharField(
        required=False,
        help_text="Code of Classgroup to Request membership for",
    )


class ReadClassGroupMemberSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = ClassGroupStudentInviteOrRequest
        fields = "__all__"
