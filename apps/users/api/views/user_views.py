from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.decorators import try_except_http_error_decorator
from apps.core.exceptions import (
    NoneExistenceError,
    UnmatchedFieldsError,
    UrlParameterError,
)
from apps.core.helpers import RequestFieldsChecker, create_200
from apps.core.permissions import IsAuthenticatedCustom, IsOwner, IsPasswordMatching
from apps.users.api.serializers import (
    ActivateSerializer,
    ChangePasswordSerializer,
    DeactivateSerializer,
    DeleteUserSerializer,
    UpdateUserSerializer,
    UserSerializer,
)
from apps.users.models import CustomUser
from apps.users.utils import DbExistenceChecker, EmailSender

##################################
##          RETRIEVE
##################################


class UserDetailView(APIView):
    """ """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedCustom, IsOwner]

    @try_except_http_error_decorator
    def get(self, request, *args, **kwargs):
        """ """

        url_username = kwargs["username"]
        if url_username:
            checker = DbExistenceChecker()

            try:
                # check and get user
                user_instance = checker.check_return_user_existence(
                    username=url_username
                )
                # check owner
                self.check_object_permissions(request, user_instance)

                # serialize data
                serializer = UserSerializer(user_instance)

                return Response(serializer.data, status=status.HTTP_200_OK)

            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                raise NoneExistenceError(
                    status_code=400,
                    message="Non existence",
                    verbose=f"Account with username `{url_username}` credentials does not exist!",
                    cause=request,
                )
        else:
            raise UrlParameterError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Url parameter wrong",
                cause=request,
                verbose='"username" must be provided',
            )


##################################
##          UPDATE
##################################


class UpdateUserView(APIView):
    """ """

    serializer_class = UpdateUserSerializer
    permission_classes = [IsAuthenticatedCustom, IsOwner, IsPasswordMatching]
    field_options = ["username", "email", "active"]
    required_fields = ["current_password"]
    message = ""

    @try_except_http_error_decorator
    def patch(self, request, *args, **kwargs):
        """ """

        url_username = kwargs["username"]
        data = request.data

        # check fields

        if url_username:

            # check fields
            r_checker = RequestFieldsChecker()
            checker = DbExistenceChecker()

            r_checker.check_required_field_or_raise(data, self.required_fields)
            r_checker.check_at_least_one_field_or_raise(data, self.field_options)
            r_checker.check_extra_fields_or_raise(
                data, self.field_options, self.required_fields
            )

            # check user existence
            try:
                user_to_update = checker.check_return_user_existence(
                    username=url_username
                )
                if user_to_update != request.user:
                    raise PermissionDenied(
                        code="Permission Denied",
                        detail="Target account does not belong to authenticated user",
                    )

            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                raise NoneExistenceError(
                    status_code=400,
                    message="Non existence",
                    verbose=f"Account with username `{url_username}` credentials does not exist!",
                    cause=request,
                )

            # update

            self.check_object_permissions(request, user_to_update)

            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            updated_user = serializer.update_user(user_to_update, **data)

            if data.get("email", False):
                EmailSender().send_email_verification_mail(request, updated_user)

                return Response(
                    create_200(
                        status.HTTP_202_ACCEPTED,
                        "User Updated",
                        f"""Account with username `{url_username}` updated to new credentials! 
                        Since new email has been provided, please verify the email to use account again""",
                    ),
                    status=status.HTTP_202_ACCEPTED,
                )

            return Response(
                create_200(
                    status.HTTP_202_ACCEPTED,
                    "User Updated",
                    f"Account with username `{url_username}` updated to new credentials! {self.message}",
                ),
                status=status.HTTP_202_ACCEPTED,
            )

            # TODO create activity

        else:
            raise UrlParameterError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Url parameter wrong",
                verbose='"username" must be provided',
                cause=request,
            )


class ChangePasswordView(UpdateUserView):
    """ """

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticatedCustom, IsOwner, IsPasswordMatching]
    field_options = ["password", "current_password"]
    required_fields = field_options
    message = "Password successfully changed."


class DeactivateUserView(UpdateUserView):
    """ """

    serializer_class = DeactivateSerializer
    permission_classes = [IsAuthenticatedCustom, IsOwner, IsPasswordMatching]
    field_options = ["active", "current_password"]
    required_fields = field_options
    message = "User account has been deactivated."


class ActivateUserView(APIView):
    """ """

    permission_classes = [AllowAny]
    serializer_class = ActivateSerializer
    field_options = ["username", "email"]
    required_fields = ["current_password"]
    message = "User account has been reactivated."

    def get(self, request):
        return Response("Activate page")

    @try_except_http_error_decorator
    def post(self, request, *args, **kwargs):
        """ """

        data = request.data

        # check fields
        r_checker = RequestFieldsChecker()
        checker = DbExistenceChecker()

        r_checker.check_required_field_or_raise(data, self.required_fields)
        r_checker.check_extra_fields_or_raise(
            data, self.field_options, self.required_fields
        )

        # check user existence
        try:
            if data.__contains__("username"):
                username_user = checker.check_return_user_existence(
                    username=data.get("username")
                )
                user_to_activate = username_user

            if data.__contains__("email"):
                email_user = checker.check_return_user_existence(
                    email=data.get("email")
                )
                user_to_activate = email_user

            if data.__contains__("email") and data.__contains__("username"):
                if username_user.id != email_user.id:
                    raise UnmatchedFieldsError(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Unmatched fields",
                        verbose="Provided fields email and username are not associated with same user",
                    )

            if user_to_activate.check_password(data.get("current_password")):
                CustomUser.objects.update_user(user_to_activate.id, active=True)
                return Response(
                    create_200(
                        status.HTTP_202_ACCEPTED,
                        "User Updated",
                        f"{user_to_activate.username} account has been activated!",
                    ),
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                raise PermissionDenied(
                    code="Permission Denied",
                    detail="Password incorrect",
                )

        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise NoneExistenceError(
                status_code=400,
                message="Non existence",
                verbose=f"Account with given credentials does not exist!",
                cause=request,
            )


##################################
##          DELETE
##################################


class DeleteUserView(APIView):
    """ """

    permission_classes = [IsAuthenticatedCustom, IsOwner, IsPasswordMatching]
    serializer_class = DeleteUserSerializer
    field_options = ["current_password"]
    required_fields = ["current_password"]

    @try_except_http_error_decorator
    def delete(self, request, *args, **kwargs):
        """ """

        url_username = kwargs["username"]
        data = request.data

        if url_username:

            # check fields
            r_checker = RequestFieldsChecker()
            checker = DbExistenceChecker()

            r_checker.check_required_field_or_raise(data, self.required_fields)
            r_checker.check_extra_fields_or_raise(
                data, self.field_options, self.required_fields
            )

            # check user existence
            try:
                user_to_delete = checker.check_return_user_existence(
                    username=url_username
                )
                # check object permissions
                self.check_object_permissions(request, user_to_delete)

                # update fields
                user_to_delete.delete()

                #  send email TODO

                return Response(
                    create_200(
                        status.HTTP_202_ACCEPTED,
                        "User Deleted",
                        f"Account with username `{url_username}` deleted!",
                    ),
                    status=status.HTTP_202_ACCEPTED,
                )

            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                raise NoneExistenceError(
                    status_code=400,
                    message="Non existence",
                    verbose=f"Account with username `{url_username}` credentials does not exist!",
                    cause=request,
                )

        else:
            raise UrlParameterError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Url parameter wrong",
                verbose='"username" must be provided',
                cause=request,
            )


# FIXME refactor using init
