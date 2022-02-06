# from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import (
    ExtraFieldsError,
    MissingFieldsError,
    NoneExistenceError,
    PreExistenceError,
    UnmatchedFieldsError,
    UrlParameterError,
)
from apps.core.helpers import (
    RequestFieldsChecker,
    create_200,
    create_400,
    create_500,
)
from apps.core.permissions import IsOwner, IsPasswordMatching
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
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, *args, **kwargs):
        """ """

        try:
            url_username = kwargs["username"]
            if url_username:
                try:
                    checker = DbExistenceChecker()
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
                        url_username,
                        create_400(
                            400,
                            "Non existence",
                            f"Account with username `{url_username}` credentials does not exist!",
                        ),
                    )
            else:
                raise UrlParameterError(
                    instance=request,
                    message=create_400(
                        status.HTTP_400_BAD_REQUEST,
                        "Url parameter wrong",
                        '"username" must be provided',
                    ),
                )

        except (UrlParameterError, NoneExistenceError) as error:
            return Response(error.message, status=error.message["status"])
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
                    verbose=f"Could not fetch user profile for `{url_username}` due to an internal error.",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


##################################
##          UPDATE
##################################


class UpdateUserView(APIView):
    """ """

    serializer_class = UpdateUserSerializer
    permission_classes = [IsAuthenticated, IsOwner, IsPasswordMatching]
    field_options = ["username", "email", "active"]
    required_fields = ["current_password"]
    message = ""

    def patch(self, request, *args, **kwargs):
        """ """

        try:
            url_username = kwargs["username"]
            data = request.data

            # self.create_responses(request, *args, **kwargs)

            if url_username:
                # check fields
                RequestFieldsChecker().check_required_field_or_raise(
                    data, self.required_fields
                )
                RequestFieldsChecker().check_at_least_one_field_or_raise(
                    data, self.field_options
                )
                RequestFieldsChecker().check_extra_fields_or_raise(
                    data, self.field_options, self.required_fields
                )

                # check user existence
                try:
                    user_to_update = DbExistenceChecker().check_return_user_existence(
                        username=url_username
                    )
                    if user_to_update != request.user:
                        raise PermissionDenied(
                            code="Permission Denied",
                            detail="Target account does not belong to authenticated user",
                        )

                except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                    raise NoneExistenceError(
                        url_username,
                        create_400(
                            400,
                            "Non existence",
                            f"Account with username `{url_username}` credentials does not exist!",
                        ),
                    )

                # update
                # check object permissions
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
                            Since new email has been provided, please verifythe email to use account again""",
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
                    instance=request,
                    message=create_400(
                        status.HTTP_400_BAD_REQUEST,
                        "Url parameter wrong",
                        '"username" must be provided',
                    ),
                )

        except (
            UrlParameterError,
            PreExistenceError,
            MissingFieldsError,
            ExtraFieldsError,
            NoneExistenceError,
        ) as error:
            return Response(error.message, status=status.HTTP_400_BAD_REQUEST)

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
                    verbose=f"Could not update credentials for user `{url_username}` due to an unknown error.",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChangePasswordView(UpdateUserView):
    """ """

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated, IsOwner, IsPasswordMatching]
    field_options = ["password", "current_password"]
    required_fields = field_options
    message = "Password successfully changed."


class DeactivateUserView(UpdateUserView):
    """ """

    serializer_class = DeactivateSerializer
    permission_classes = [IsAuthenticated, IsOwner, IsPasswordMatching]
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

    def post(self, request, *args, **kwargs):
        """ """

        try:
            data = request.data

            # check fields
            RequestFieldsChecker().check_required_field_or_raise(
                data, self.required_fields
            )
            RequestFieldsChecker().check_extra_fields_or_raise(
                data, self.field_options, self.required_fields
            )

            # check user existence
            try:
                if data.__contains__("username"):
                    username_user = DbExistenceChecker().check_return_user_existence(
                        username=data.get("username")
                    )
                    user_to_activate = username_user

                if data.__contains__("email"):
                    email_user = DbExistenceChecker().check_return_user_existence(
                        email=data.get("email")
                    )
                    user_to_activate = email_user

                if data.__contains__("email") and data.__contains__("username"):
                    if username_user.id != email_user.id:
                        raise UnmatchedFieldsError(
                            request,
                            create_400(
                                status.HTTP_400_BAD_REQUEST,
                                "Unmatched fields",
                                "Provided fields email and username are not associated with same user",
                            ),
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
                    request.data,
                    create_400(
                        400,
                        "Non existence",
                        f"Account with given credentials does not exist!",
                    ),
                )

        except (
            UrlParameterError,
            PreExistenceError,
            MissingFieldsError,
            ExtraFieldsError,
            NoneExistenceError,
            UnmatchedFieldsError,
        ) as error:
            return Response(error.message, status=status.HTTP_400_BAD_REQUEST)

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
                    verbose=f"Could not activate user {user_to_activate.username} due to an unknown error.",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


##################################
##          DELETE
##################################


class DeleteUserView(APIView):
    """ """

    permission_classes = [IsAuthenticated, IsOwner, IsPasswordMatching]
    serializer_class = DeleteUserSerializer
    field_options = ["current_password"]
    required_fields = ["current_password"]

    def delete(self, request, *args, **kwargs):
        """ """

        try:
            url_username = kwargs["username"]
            data = request.data

            if url_username:

                # check fields
                r_checker = RequestFieldsChecker()
                r_checker.check_required_field_or_raise(data, self.required_fields)
                r_checker.check_extra_fields_or_raise(data, self.field_options)

                # check user existence
                try:
                    checker = DbExistenceChecker()
                    user_to_delete = checker.check_return_user_existence(
                        username=url_username
                    )
                    # check object permissions
                    self.check_object_permissions(request, user_to_delete)

                    # update fields
                    user_to_delete.delete()

                    #  send email

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
                        url_username,
                        create_400(
                            400,
                            "Non existence",
                            f"Account with username `{url_username}` credentials does not exist!",
                        ),
                    )

            else:
                raise UrlParameterError(
                    instance=request,
                    message=create_400(
                        status.HTTP_400_BAD_REQUEST,
                        "Url parameter wrong",
                        '"username" must be provided',
                    ),
                )

        except (
            UrlParameterError,
            NoneExistenceError,
            MissingFieldsError,
            ExtraFieldsError,
            PreExistenceError,
        ) as error:
            return Response(error.message, status=status.HTTP_400_BAD_REQUEST)

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
                    verbose=f"Could not delete account of user {url_username} due to an unknown error.",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# FIXME refactor using init
