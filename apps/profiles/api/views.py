from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import (
    ExtraFieldsError,
    MissingFieldsError,
    NoneExistenceError,
    UrlParameterError,
)
from apps.core.helpers import create_200, create_400, create_500
from apps.core.permissions import IsProfileOwner, IsProfilePasswordMatching
from apps.profiles.utils import check_fields, get_profile_from_url_username_or_raise

from .serializers import (
    ChangePrivateProfileSerializer,
    ProfileImagesSerializer,
    ProfileOwnerSerializer,
    ProfilePrivateSerializer,
    ProfilePublicSerializer,
    ProfileSummarySerializer,
    UpdateProfileSerializer,
)


class ProfileDetailView(APIView):
    """ """

    serializer_class = ProfilePublicSerializer
    owner_serializer_class = ProfileOwnerSerializer
    alternative_serializer_class = ProfilePrivateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        """ """

        try:
            profile_instance = get_profile_from_url_username_or_raise(**kwargs)
            self.check_object_permissions(request, profile_instance)
            # check owner
            if request.user.id == profile_instance.user.id:
                serializer = self.owner_serializer_class(profile_instance)
            # if not owner
            else:
                # private
                if profile_instance.private:
                    # follower
                    if request.user.id in profile_instance.user.user_follower.follower:
                        serializer = self.serializer_class(profile_instance)
                    else:
                        serializer = self.alternative_serializer_class(profile_instance)
                # public
                else:
                    serializer = self.serializer_class(profile_instance)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except (UrlParameterError, NoneExistenceError) as error:
            return Response(error.message, status=error.message.get("status"))

        except (PermissionDenied, NotAuthenticated) as error:
            return Response(
                create_400(
                    error.status_code,
                    error.get_codes(),
                    error.get_full_details().get("message"),
                ),
                status=error.status_code,
            )

        except Exception as error:
            return Response(
                create_500(
                    cause=error.args[0] or None,
                    verbose=f"Could not get details for `{kwargs.get('username')}` due to an unknown error",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProfileSummaryView(APIView):

    serializer_class = ProfileSummarySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        """ """

        try:
            profile_instance = get_profile_from_url_username_or_raise(**kwargs)
            self.check_object_permissions(request, profile_instance)
            serializer = self.serializer_class(profile_instance)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except (UrlParameterError, NoneExistenceError) as error:
            return Response(error.message, status=error.message.get("status"))

        except (PermissionDenied, NotAuthenticated) as error:
            return Response(
                create_400(
                    error.status_code,
                    error.get_codes(),
                    error.get_full_details().get("message"),
                ),
                status=error.status_code,
            )

        except Exception as error:
            return Response(
                create_500(
                    cause=error.args[0] or None,
                    verbose=f"Could not get details for `{kwargs.get('username')}` due to an unknown error",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateProfileView(APIView):
    """
    Update User Profile

    Method
    ---
    patch:

    - field_options = [
        "bio",
        "name",
        "nickname",
        "dob" / ISO 8601: `2013-01-29T12:34:56.000000Z` /,
        "location",
        "phone",
        "use_persona",
        "persona",
    ]
    - required_fields = ["current_password"]
    """

    serializer_class = UpdateProfileSerializer
    permission_classes = [
        IsAuthenticated,
        IsProfileOwner,
        # IsProfilePasswordMatching,
    ]
    required_fields = None
    # required_fields = ["current_password"]
    field_options = [
        "bio",
        "name",
        "nickname",
        "dob",
        "location",
        "phone",
        "use_persona",
        "persona",
        "current_password",
    ]

    def patch(self, request, *args, **kwargs):
        """ """

        try:
            data = request.data

            profile_to_update = get_profile_from_url_username_or_raise(**kwargs)
            check_fields(data, self.field_options, self.required_fields)
            self.check_object_permissions(request, profile_to_update)

            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.update_profile(profile_to_update, **serializer.validated_data)

            return Response(
                create_200(
                    status.HTTP_200_OK,
                    "Profile Updated",
                    f"Profile credentials of user `{kwargs.get('username')}` has been updated.",
                ),
                status=status.HTTP_200_OK,
            )

        except (
            UrlParameterError,
            NoneExistenceError,
            ExtraFieldsError,
            MissingFieldsError,
        ) as error:
            return Response(error.message, status=error.message.get("status"))

        except (PermissionDenied, NotAuthenticated) as error:
            return Response(
                create_400(
                    error.status_code,
                    error.get_codes(),
                    error.get_full_details().get("message"),
                ),
                status=error.status_code,
            )

        except Exception as error:
            return Response(
                create_500(
                    cause=error.args[0] or None,
                    verbose=f"Could not update credentials for `{kwargs.get('username')}` due to an unknown error",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChangePrivateProfileView(APIView):
    """
    Change profile `private` field for privacy

    Method
    ---
    post:
    - required_fields = ["current_password"]
    - field_options = None
    """

    serializer_class = ChangePrivateProfileSerializer
    permission_classes = [
        IsAuthenticated,
        IsProfileOwner,
        # IsProfilePasswordMatching,
    ]
    required_fields = None
    # required_fields = ["current_password"]
    field_options = ["current_password"]

    def post(self, request, *args, **kwargs):
        """ """

        try:
            data = request.data

            profile_to_update = get_profile_from_url_username_or_raise(**kwargs)
            check_fields(data, self.field_options, self.required_fields)
            self.check_object_permissions(request, profile_to_update)

            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            private = serializer.change_private(profile_to_update)

            return Response(
                create_200(
                    status.HTTP_200_OK,
                    "Profile Updated",
                    f"Profile of user `{kwargs.get('username')}` has turned privacy to {private}",
                ),
                status=status.HTTP_200_OK,
            )

        except (
            UrlParameterError,
            NoneExistenceError,
            MissingFieldsError,
            ExtraFieldsError,
        ) as error:
            return Response(error.message, status=error.message.get("status"))

        except (PermissionDenied, NotAuthenticated) as error:
            return Response(
                create_400(
                    error.status_code,
                    error.get_codes(),
                    error.get_full_details().get("message"),
                ),
                status=error.status_code,
            )

        except Exception as error:
            return Response(
                create_500(
                    cause=error.args[0] or None,
                    verbose=f"Could not make private `{kwargs.get('username')}` due to an unknown error",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProfileImageUploadView(APIView):
    """
    Upload profile images

    Method
    ---
    post:
    - required_fields = None
    - field_options = ["avatar", "cover"]
    """

    serializer_class = ProfileImagesSerializer
    permission_classes = [
        IsAuthenticated,
        IsProfileOwner,
    ]
    required_fields = None
    field_options = ["avatar", "cover"]

    def check_images(self, data):
        """ """

        avatar = data.get("avatar", False)
        cover = data.get("cover", False)

        if not avatar and not cover:
            raise MissingFieldsError(
                "fields",
                create_400(
                    400,
                    "Missing fields",
                    "Either one of the `avatar` or `cover` fields must be provided",
                ),
            )

    def post(self, request, *args, **kwargs):
        """ """

        try:
            profile_instance = get_profile_from_url_username_or_raise(**kwargs)
            self.check_object_permissions(request, profile_instance)
            data = request.data

            #  check images
            self.check_images(data)

            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            updated_user = serializer.update(
                profile_instance, serializer.validated_data
            )

            return Response(
                create_200(
                    status.HTTP_200_OK,
                    "Profile Updated",
                    f"""Profile picture of user `{kwargs.get('username')}` updated. 
                    Now: 
                    `avatar={updated_user.avatar.path}`, 
                    `cover={updated_user.cover.path}`""",
                ),
                status=status.HTTP_200_OK,
            )

        except (UrlParameterError, NoneExistenceError, MissingFieldsError) as error:
            return Response(error.message, status=error.message.get("status"))

        except (PermissionDenied, NotAuthenticated) as error:
            return Response(
                create_400(
                    error.status_code,
                    error.get_codes(),
                    error.get_full_details().get("message"),
                ),
                status=error.status_code,
            )

        except Exception as error:
            return Response(
                create_500(
                    cause=error.args[0] or None,
                    verbose=f"Could not make private `{kwargs.get('username')}` due to an unknown error",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EnableDisablePersonaView(APIView):
    """
    Update User Profile

    Method
    ---
    patch:

    - field_options = [
    ]
    - required_fields = ["current_password"]
    """

    serializer_class = UpdateProfileSerializer
    permission_classes = [
        IsAuthenticated,
        IsProfileOwner,
        # IsProfilePasswordMatching,
    ]
    required_fields = None
    field_options = None
    # required_fields = ["current_password"]
    # field_options = ["current_password"]

    def patch(self, request, *args, **kwargs):
        """ """

        try:
            data = request.data

            profile_to_update = get_profile_from_url_username_or_raise(**kwargs)
            check_fields(data, self.field_options, self.required_fields)
            self.check_object_permissions(request, profile_to_update)

            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)

            persona_enabled = profile_to_update.use_persona
            profile_to_update.use_persona = not persona_enabled
            profile_to_update.save()

            return Response(
                create_200(
                    status.HTTP_200_OK,
                    "Profile Updated",
                    f"Profile credentials of user `{kwargs.get('username')}` has been updated. Use_persona set to {not persona_enabled}",
                ),
                status=status.HTTP_200_OK,
            )

        except (
            UrlParameterError,
            NoneExistenceError,
            ExtraFieldsError,
            MissingFieldsError,
        ) as error:
            return Response(error.message, status=error.message.get("status"))

        except (PermissionDenied, NotAuthenticated) as error:
            return Response(
                create_400(
                    error.status_code,
                    error.get_codes(),
                    error.get_full_details().get("message"),
                ),
                status=error.status_code,
            )

        except Exception as error:
            return Response(
                create_500(
                    cause=error.args[0] or None,
                    verbose=f"Could not update credentials for `{kwargs.get('username')}` due to an unknown error",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SetPersonaView(APIView):
    """
    Update User Profile

    Method
    ---
    patch:

    - field_options = [
        "persona",
    ]
    - required_fields = ["current_password"]
    """

    serializer_class = UpdateProfileSerializer
    permission_classes = [
        IsAuthenticated,
        IsProfileOwner,
        # IsProfilePasswordMatching,
    ]
    required_fields = [
        # "current_password",
        "persona"
    ]
    field_options = ["persona"]

    def patch(self, request, *args, **kwargs):
        """ """

        try:
            data = request.data

            profile_to_update = get_profile_from_url_username_or_raise(**kwargs)
            check_fields(data, self.field_options, self.required_fields)
            self.check_object_permissions(request, profile_to_update)

            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.update_profile(profile_to_update, **serializer.validated_data)

            return Response(
                create_200(
                    status.HTTP_200_OK,
                    "Profile Updated",
                    f"Profile credentials of user `{kwargs.get('username')}` has been updated. Persona has been set to {data['persona']}",
                ),
                status=status.HTTP_200_OK,
            )

        except (
            UrlParameterError,
            NoneExistenceError,
            ExtraFieldsError,
            MissingFieldsError,
        ) as error:
            return Response(error.message, status=error.message.get("status"))

        except (PermissionDenied, NotAuthenticated) as error:
            return Response(
                create_400(
                    error.status_code,
                    error.get_codes(),
                    error.get_full_details().get("message"),
                ),
                status=error.status_code,
            )

        except Exception as error:
            return Response(
                create_500(
                    cause=error.args[0] or None,
                    verbose=f"Could not update credentials for `{kwargs.get('username')}` due to an unknown error",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
