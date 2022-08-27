from rest_framework import serializers

from apps.class_groups.api.serializers import ClassGroupSerializer
from apps.classrooms.models import Classroom, ClassroomInviteOrRequest
from apps.core.decorators import try_except_http_error_decorator
from apps.core.exceptions import UnknownModelFieldsError
from apps.users.api.serializers import UserSerializer

#########################
#   CLASS GROUP
#########################


class ClassroomOnlySerializer(serializers.ModelSerializer):
    """Serializer for Classroom"""

    class Meta:
        model = Classroom
        fields = "__all__"


class ClassroomSerializer(serializers.ModelSerializer):
    """Serializer for Classroom"""

    teacher = UserSerializer(source="_created_by")

    class Meta:
        model = Classroom
        fields = "__all__"


class PublicClassroomSerializer(serializers.ModelSerializer):
    """Serializer for Classroom"""

    teacher = UserSerializer(source="_created_by")

    class Meta:
        model = Classroom
        fields = (
            "teacher",
            "name",
            "subject",
            "classroom_code",
            "archive",
            "id",
            "_created_date",
            "_modified_date",
            "_created_by",
        )


class CreateClassroomSerializer(serializers.ModelSerializer):
    """Serializer for Creating Classroom"""

    name = serializers.CharField(
        max_length=200,
        required=True,
        help_text="Name for the classroom",
    )
    subject = serializers.CharField(
        max_length=100,
        required=True,
        help_text="Name of subject. E.g. COMP302, MGTS102, etc.",
    )

    class Meta:
        model = Classroom
        fields = (
            "name",
            "subject",
        )


class UpdateClassroomSerializer(serializers.ModelSerializer):
    """Serializer for Updating Classroom"""

    name = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Name for the classroom",
    )
    subject = serializers.CharField(
        max_length=100,
        required=False,
        help_text="Name of subject. E.g. COMP302, MGTS102, etc.",
    )

    class Meta:
        model = Classroom
        fields = (
            "name",
            "subject",
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


class CreateInviteClassroomMemberSerializer(serializers.Serializer):
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
    classroom_id = serializers.IntegerField(
        required=False,
        help_text="Id of Classroom to Invite to",
    )
    classroom_code = serializers.CharField(
        required=False,
        help_text="Code of Classroom to Invite to",
    )
    classgroup_id = serializers.IntegerField(
        required=False,
        help_text="Id of Classgroup to Invite to",
    )
    classgroup_code = serializers.CharField(
        required=False,
        help_text="Code of Classgroup to Invite to",
    )
    target_type = serializers.CharField(
        required=True, help_text="Target type i.e. S, T, C"
    )


class CreateRequestClassroomMemberSerializer(serializers.Serializer):
    """"""

    classroom_id = serializers.IntegerField(
        required=False,
        help_text="Id of Classroom to Request membership for",
    )
    classroom_code = serializers.CharField(
        required=False,
        help_text="Code of Classroom to Request membership for",
    )
    target_type = serializers.CharField(
        required=True, help_text="Code of Classroom to Invite to"
    )


class ReadClassroomMemberSerializer(serializers.ModelSerializer):
    """"""

    student = UserSerializer(required=False)
    teacher = UserSerializer(required=False)
    classgroup = ClassGroupSerializer(required=False)

    class Meta:
        model = ClassroomInviteOrRequest
        fields = "__all__"
