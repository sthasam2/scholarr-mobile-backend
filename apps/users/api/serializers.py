from django.db.models.fields import EmailField
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.core.exceptions import CustomAuthenticationFailed, NotAuthenticatedError
from apps.core.helpers import create_400

from ..models import CustomUser
from ..utils import DbExistenceChecker

##########################
#          AUTH
##########################


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Model Serializer for creating CustomUser model
    """

    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text="Username. example: sam_smith",
        style={"input_type": "text", "placeholder": "Username"},
    )
    email = serializers.EmailField(
        max_length=150,
        required=True,
        help_text="Email address. example: example@example.domain",
        style={"input_type": "email", "placeholder": "Email"},
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="New password for ",
        style={"input_type": "password", "placeholder": "Password"},
    )

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "username",
            "password",
        ]

    def create(self, validated_data):
        """
        Creates a user instance in the database using valiadted fields

        Disclaimer: Please use validated data!
        """

        created_user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return created_user


class SendEmailVerificationSerializer(serializers.Serializer):
    """ """

    email = serializers.EmailField(help_text="Email for verification resend")


class LogoutSerializer(serializers.Serializer):
    """ """

    refresh_token = serializers.CharField(
        help_text="Refresh token used for obtaining access token"
    )


class SendResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=150,
        required=True,
        help_text="Email address of account for resetting password",
        style={"input_type": "email", "placeholder": "Email"},
    )


class ConfirmResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=150,
        required=True,
        help_text="Email address of account for resetting password",
        style={"input_type": "email", "placeholder": "Email"},
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="New password for given user",
        style={"input_type": "password", "placeholder": "Password"},
    )
    token = serializers.CharField(
        max_length=150,
        required=True,
        help_text="Token for resetting password sent in the mail",
        style={"input_type": "text", "placeholder": "Token"},
    )


##########################
#          JWT
##########################


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """ """

    username = serializers.CharField(max_length=150)
    password = serializers.CharField()

    class Meta:
        fields = ["username", "password"]

    @classmethod
    def get_token(cls, user):
        return super().get_token(user)

    def validate(self, attrs):
        """
        serializer validate method
        """

        # username = attrs["username"]
        # exists = DbExistenceChecker().check_username_existence
        try:
            data = super().validate(attrs)
            data["status"] = 200
            data["user_details"] = dict(
                username=self.user.username,
                email=self.user.email,
                id=self.user.id,
                email_verified=self.user.email_verified,
            )

            return data

        except NotAuthenticatedError as error:
            raise CustomAuthenticationFailed(
                cause="Autentication",
                status_code=404,
                message="Invalid username or password",
                verbose=f"Account with given credentials does not exist!",
            )

        except AuthenticationFailed as error:
            raise CustomAuthenticationFailed(
                cause="Autentication",
                status_code=404,
                message="Invalid username or password",
                verbose=f"Account with given credentials does not exist!",
            )


##########################
#          USER
##########################


class PublicUserSerializer(serializers.ModelSerializer):
    """
    Serializers for CustomUser model
    """

    class Meta:
        model = CustomUser
        fields = ["username", "email", "active", "id"]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializers for CustomUser model
    """

    class Meta:
        model = CustomUser
        fields = ["username", "email", "registered_date", "active", "id"]


class UpdateUserSerializer(serializers.ModelSerializer):
    """
    Serializers for CustomUser model
    """

    username = serializers.CharField(
        max_length=150,
        required=False,
        help_text="Username. example: sam_smith",
        style={"input_type": "text", "placeholder": "Username"},
    )
    email = serializers.EmailField(
        max_length=150,
        required=False,
        help_text="Email address. example: example@example.domain",
        style={"input_type": "email", "placeholder": "Email"},
    )
    active = serializers.BooleanField(
        required=False, help_text="Activate/Deactivate account"
    )
    current_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Current password ",
        style={"input_type": "password", "placeholder": "Current Password"},
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "active", "current_password"]

    def update_user(self, user_instance, **validated_data):
        """ """

        return CustomUser.objects.update_user(user_instance.id, **validated_data)


class ChangePasswordSerializer(serializers.ModelSerializer):
    """ """

    current_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Current password ",
        style={"input_type": "password", "placeholder": "Current Password"},
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="New password ",
        style={"input_type": "password", "placeholder": "New Password"},
    )

    class Meta:
        model = CustomUser
        fields = ["current_password", "password"]

    def update_user(self, user_instance, **validated_data):
        """ """

        return CustomUser.objects.update_user(user_instance.id, **validated_data)


class DeactivateSerializer(serializers.ModelSerializer):
    """ """

    current_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Current password ",
        style={"input_type": "password", "placeholder": "Current Password"},
    )
    active = serializers.BooleanField(
        write_only=True,
        required=True,
        help_text="Activate or Decativate the account. True for activate, False for Deactivate",
        style={"input_type": "text", "placeholder": "Activate/Deactivate"},
    )

    class Meta:
        model = CustomUser
        fields = ["active", "current_password"]

    def update_user(self, user_instance, **validated_data):
        """ """

        return CustomUser.objects.update_user(user_instance.id, **validated_data)


class ActivateSerializer(serializers.Serializer):
    """ """

    current_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Current password ",
        style={"input_type": "password", "placeholder": "Current Password"},
    )
    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text="Username. example: sam_smith",
        style={"input_type": "text", "placeholder": "Username"},
    )
    email = serializers.EmailField(
        max_length=150,
        required=True,
        help_text="Email address. example: example@example.domain",
        style={"input_type": "email", "placeholder": "Email"},
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "current_password",
        ]


class DeleteUserSerializer(serializers.ModelSerializer):
    """ """

    current_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Current password ",
        style={"input_type": "password", "placeholder": "Current Password"},
    )

    class Meta:
        model = CustomUser
        fields = ["current_password"]
