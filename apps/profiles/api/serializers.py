from rest_framework import serializers

from apps.core.exceptions import UnknownModelFieldsError
from apps.profiles.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """ """

    user_id = serializers.IntegerField(source="user.id")
    username = serializers.CharField(source="user.username")
    email = serializers.EmailField(source="user.email")
    created_date = serializers.DateTimeField()
    updated_date = serializers.DateTimeField()
    account_verified = serializers.BooleanField()
    use_persona = serializers.BooleanField()
    persona = serializers.IntegerField()
    avatar = serializers.ImageField()
    cover = serializers.ImageField()
    bio = serializers.CharField(
        help_text="What's on your mind?",
    )
    name = serializers.CharField(
        help_text="Full Name. For eg. Will Smith ",
    )
    nickname = serializers.CharField(
        help_text="Nickname. The name you want to be called. For eg. Will",
    )
    dob = serializers.DateTimeField(
        style={"input_type": "datetime-local", "placeholder": "Date and Time of birth"},
        help_text="The date and time of your birth",
    )
    location = serializers.CharField(
        help_text="User Location. Street, Municipality/VDC, State, Country",
    )
    phone = serializers.CharField(
        help_text="Contact digits. eg. +97798XXYYZZWW",
    )
    phone_verified = serializers.BooleanField(
        help_text="Contact number verified",
    )
    private = serializers.BooleanField(help_text="Profile Privacy")
    # notifications
    #  connections
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    muted_count = serializers.SerializerMethodField()
    blocked_count = serializers.SerializerMethodField()

    class Meta:
        abstract = True
        model = Profile
        fields = [
            "user_id",
            "username",
            "created_date",
            "updated_date",
            "account_verified",
            "use_persona",
            "persona",
            "avatar",
            "cover",
            "bio",
            "name",
            "nickname",
            "dob",
            "location",
            "phone",
            "phone_verified",
            "email",
            "private",
            "followers_count",
            "following_count",
            "muted_count",
            "blocked_count",
        ]


class ProfileOwnerSerializer(ProfileSerializer):
    """ """

    class Meta:
        model = Profile
        fields = [
            "user_id",
            "username",
            "created_date",
            "updated_date",
            "account_verified",
            "use_persona",
            "persona",
            "avatar",
            "cover",
            "bio",
            "name",
            "nickname",
            "dob",
            "location",
            "phone",
            "phone_verified",
            "email",
            "private",
            "followers_count",
            "following_count",
            "muted_count",
            "blocked_count",
        ]


class ProfilePublicSerializer(ProfileSerializer):
    """ """

    class Meta:
        model = Profile
        fields = [
            "username",
            "account_verified",
            "use_persona",
            "persona",
            "avatar",
            "cover",
            "bio",
            "name",
            "nickname",
            "dob",
            "location",
            "phone",
            "phone_verified",
            "email",
            "followers_count",
            "following_count",
        ]


class ProfilePrivateSerializer(ProfileSerializer):
    """ """

    class Meta:
        model = Profile
        fields = [
            "user_id",
            "username",
            "account_verified",
            "use_persona",
            "persona",
            "avatar",
            "cover",
            "nickname",
            "private",
        ]


class ProfileSummarySerializer(ProfileSerializer):
    """ """

    class Meta:
        model = Profile
        fields = [
            "user_id",
            "username",
            "account_verified",
            "use_persona",
            "persona",
            "avatar",
            "cover",
            "nickname",
            "private",
        ]


class UpdateProfileSerializer(serializers.ModelSerializer):
    """ """

    bio = serializers.CharField(
        required=False,
        help_text="What's on your mind?",
    )
    name = serializers.CharField(
        required=False,
        help_text="Full Name. For eg. Will Smith ",
    )
    nickname = serializers.CharField(
        required=False,
        help_text="Nickname. The name you want to be called. For eg. Will",
    )
    dob = serializers.DateTimeField(
        required=False,
        style={"input_type": "datetime-local", "placeholder": "Date and Time of birth"},
        help_text="The date and time of your birth",
    )
    location = serializers.CharField(
        required=False,
        help_text="User Location. Street, Municipality/VDC, State, Country",
    )
    phone = serializers.CharField(
        required=False,
        help_text="Contact digits. eg. +97798XXYYZZWW",
    )
    current_password = serializers.CharField(
        write_only=True,
        required=False,
        # required=True,
        help_text="Current password ",
        style={"input_type": "password", "placeholder": "Current Password"},
    )
    use_persona = serializers.BooleanField(
        required=False,
        help_text="Enable Diable Persona",
    )
    persona = serializers.IntegerField(
        required=False,
        help_text="The persona to use",
    )

    class Meta:
        model = Profile
        fields = [
            "bio",
            "name",
            "nickname",
            "dob",
            "location",
            "phone",
            "current_password",
            "use_persona",
            "persona",
        ]

    def update_profile(self, profile_instance, **validated_data):
        """ """
        try:
            if validated_data.get("current_password", False):
                validated_data.pop("current_password")
            for key, value in validated_data.items():
                if profile_instance.__dict__.__contains__(key):
                    if profile_instance.__getattribute__(key) != value:
                        profile_instance.__setattr__(key, value)
                else:
                    raise UnknownModelFieldsError(
                        key,
                        f"'{profile_instance.__class__.__name__}' object has no model field called {key}",
                    )

            profile_instance.save()

        except UnknownModelFieldsError as error:
            print(error)
            raise error

        except Exception as error:
            print("ERROR @update_profile\n", error)
            raise error


class ChangePrivateProfileSerializer(serializers.ModelSerializer):
    """ """

    current_password = serializers.CharField(
        write_only=True,
        required=False,
        # required=True,
        help_text="Current password ",
        style={"input_type": "password", "placeholder": "Current Password"},
    )

    class Meta:
        model = Profile
        fields = [
            "current_password",
        ]

    def change_private(self, profile_instance):
        """ """
        try:
            new_private = not profile_instance.private
            profile_instance.private = new_private
            profile_instance.save()
            return new_private

        except UnknownModelFieldsError as error:
            print(error)
            raise error

        except Exception as error:
            print("ERROR @change_private\n", error)
            raise error


class ProfileImagesSerializer(serializers.ModelSerializer):
    """ """

    avatar = serializers.ImageField(required=False)
    cover = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ["avatar", "cover"]
