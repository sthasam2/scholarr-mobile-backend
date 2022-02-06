from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

# from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.exceptions import (
    AlreadyEmailVerifiedError,
    ExpiredError,
    MissingFieldsError,
    NoneExistenceError,
    PreExistenceError,
    UnmatchedFieldsError,
)
from apps.core.helpers import create_200, create_400, create_500
from apps.users.models import CustomUser, EmailToken
from apps.users.utils import DbExistenceChecker, EmailSender

from ..serializers import (
    ConfirmResetPasswordSerializer,
    CreateUserSerializer,
    LogoutSerializer,
    SendEmailVerificationSerializer,
    SendResetPasswordSerializer,
)
from .jwt_views import CustomTokenObtainPairView

##################################
##          CREATE
##################################


class RegisterView(CreateAPIView):
    """
    General API View for registering users

    Methods:
    @GET - Shows simple message

    @POST - Registers a user. Request body => {"email": ,"username": ,"password": }
    """

    permission_classes = [AllowAny]
    serializer_class = CreateUserSerializer

    def get(self, request, *args, **kwargs):
        """
        Register GET method
        """
        request.query_params
        return Response(
            dict(status=200, message="Register GET Page! Register an account here!")
        )

    def post(self, request, *args, **kwargs):
        """
        Register POST method
        """
        try:
            email = request.data.get("email", False)
            username = request.data.get("username", False)
            password = request.data.get("password", False)

            if email and username and password:

                if DbExistenceChecker().check_email_existence(email):
                    raise PreExistenceError(
                        email,
                        create_400(
                            status.HTTP_400_BAD_REQUEST,
                            "Already exists",
                            f'User with email "{email}" already exists. Try a different email',
                            "email",
                        ),
                    )

                if DbExistenceChecker().check_username_existence(username):
                    raise PreExistenceError(
                        username,
                        create_400(
                            status.HTTP_400_BAD_REQUEST,
                            "Already exists",
                            f'User with username "{username}" already exists. Try a different username',
                            "username",
                        ),
                    )

                serializer = CreateUserSerializer(
                    data={"email": email, "username": username, "password": password}
                )
                serializer.is_valid(raise_exception=True)
                new_user = serializer.save()

                email_sender = EmailSender()
                email_sender.send_email_verification_mail(request, new_user)

                return Response(
                    create_200(
                        201,
                        "Created",
                        f"A user account with email `{email}` and username `{username}` created!",
                    ),
                    status=status.HTTP_201_CREATED,
                )
            else:
                raise MissingFieldsError(
                    instance=request,
                    message=create_400(
                        status.HTTP_400_BAD_REQUEST,
                        "Missing Fields",
                        "Either of the required fields email, username, and/or password is missing.",
                        "request body",
                    ),
                )

        except (MissingFieldsError, PreExistenceError) as error:
            return Response(error.message, status=error.message["status"])

        except Exception as error:
            return Response(
                create_500(
                    cause=error.args[0] or None,
                    verbose=f"Could not create account due to an unknown error.",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


##################################
##          RETRIEVE
##################################


class ResendEmailVerificationView(APIView):
    """ """

    permission_classes = [AllowAny]
    serializer_class = SendEmailVerificationSerializer

    # @swagger_auto_schema(
    # responses={
    #     status.HTTP_401_UNAUTHORIZED: openapi.Response(
    #         description="Access Denied", schema=Response400Schema
    #     ),
    #     status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
    #         description="Internal Error", schema=Response500Schema
    #     ),
    #     status.HTTP_200_OK: openapi.Response(
    #         description="Login Accepted", schema=LoginAcceptedResponseSchema
    #     ),
    # },
    # )
    def post(self, request, *args, **kwargs):
        """ """
        try:
            # TODO  check last sent verification and dont allow multiple email in certain timeframe

            email = request.data.get("email", False)
            if email:

                try:
                    user_requested = DbExistenceChecker().check_return_user_existence(
                        email=email
                    )
                except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                    raise NoneExistenceError(
                        email,
                        create_400(
                            400,
                            "Non existence",
                            f"Account with email {email} credentials does not exist! Check email or sign up using a different email",
                            "email",
                        ),
                    )

                if not user_requested.email_verified:
                    email_sender = EmailSender()
                    email_sender.send_email_verification_mail(request, user_requested)

                    return Response(
                        create_200(
                            202,
                            "Email Sent",
                            f'A new verification email has been sent to email"{email}"!',
                        ),
                        status=status.HTTP_202_ACCEPTED,
                    )
                else:
                    raise AlreadyEmailVerifiedError(
                        message=create_400(
                            400,
                            "Already verified",
                            "`email` already verified.",
                            "verified",
                        ),
                    )

            else:
                raise MissingFieldsError(
                    instance=request,
                    message=create_400(
                        status.HTTP_400_BAD_REQUEST,
                        "Missing fields",
                        "`email` field is mandatory. Please provide email",
                        "reqbody:email",
                    ),
                )

        except (
            AlreadyEmailVerifiedError,
            MissingFieldsError,
            NoneExistenceError,
        ) as error:
            return Response(error.message, status=error.message["status"])

        except Exception as error:
            return Response(
                create_500(
                    verbose=f"Could not send verification email due to an unknown error.",
                    cause=error.args[0] or None,
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LoginView(CustomTokenObtainPairView):
    """ """

    permission_classes = [AllowAny]


class LogoutView(APIView):
    """ """

    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        """ """

        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

                return Response(
                    create_200(202, "Logged out", "Sucessfully logged out"),
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                raise MissingFieldsError(
                    "refresh token",
                    create_400(
                        400,
                        "Missing Fields",
                        "`refresh` must be provided with refresh token",
                        "reqbody:refresh",
                    ),
                )

        except MissingFieldsError as error:
            return Response(error.message, status=error.message.get("status"))

        except Exception as e:
            return Response(
                create_400(400, "Error occuored", e.args[0]),
                status=status.HTTP_400_BAD_REQUEST,
            )


class SendResetPasswordView(APIView):
    """ """

    permission_classes = [AllowAny]
    serializer_class = SendResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        """ """
        try:
            # TODO  check last sent verification and dont allow multiple email in certain timeframe

            email = request.data.get("email", False)
            if email:

                try:
                    user_requested = DbExistenceChecker().check_return_user_existence(
                        email=email
                    )

                except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                    raise NoneExistenceError(
                        email,
                        create_400(
                            404,
                            "Non existence",
                            f"Account with email {email} credentials does not exist!",
                            "email",
                        ),
                    )

                email_sender = EmailSender()
                email_sender.send_password_reset_email(request, user_requested)

                return Response(
                    create_200(
                        202,
                        "Email Sent",
                        f'A new password email has been sent to email"{email}"!',
                    ),
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                raise MissingFieldsError(
                    instance=request,
                    message=create_400(
                        status.HTTP_400_BAD_REQUEST,
                        "Missing fields",
                        "`email` field is mandatory. Please provide email",
                        "reqbod:email",
                    ),
                )

        except (
            AlreadyEmailVerifiedError,
            MissingFieldsError,
            NoneExistenceError,
        ) as error:
            return Response(error.message, status=error.message["status"])

        except Exception as error:
            return Response(
                create_500(
                    verbose=f"Could not send reset account password email due to an unknown error.",
                    cause=error.args[0] or None,
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


##################################
##          UPDATE
##################################


class VerifyEmailView(APIView):
    """ """

    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request, *args, **kwargs):
        """
        GET method for email activation
        """
        try:
            # get token and username
            uid = force_str(urlsafe_base64_decode(kwargs["uidb64"]))
            token = kwargs["token"]

            # check token and user existence

            try:
                user_to_verify = DbExistenceChecker().check_return_user_existence(
                    pk=uid
                )
            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                raise NoneExistenceError(
                    "User",
                    create_400(
                        404,
                        "Non existence",
                        "User associated to token does not exist",
                        "token",
                    ),
                )

            try:
                email_token = DbExistenceChecker().check_return_token_existence(
                    token=token
                )
            except (TypeError, ValueError, OverflowError, EmailToken.DoesNotExist):
                raise NoneExistenceError(
                    "Email Token",
                    create_400(400, "Non existence", "Token does not exist", "token"),
                )

            # check expired
            if email_token.check_expired:
                raise ExpiredError(
                    "Email Token",
                    create_400(400, "Expired", "Email Token already expired!", "token"),
                )

            # check token user and uid match
            if email_token.user.id != user_to_verify.id:
                raise UnmatchedFieldsError(
                    "User",
                    create_400(
                        400, "Not matching", "Url user and Token user don't match!"
                    ),
                )

            user_to_verify.email_verified = True
            user_to_verify.save()

            if request.accepted_renderer.format == "json":

                return Response(
                    create_200(
                        200,
                        "Email verified",
                        "Email has been verified. Now you can login to your account",
                    )
                )
            else:

                return Response(
                    {"user": user_to_verify},
                    template_name="users/email_verified.html",
                )

        except (NoneExistenceError, ExpiredError, UnmatchedFieldsError) as error:
            return Response(error.message, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response(
                create_500(
                    cause=error.args[0] or None,
                    verbose=f"Could not verify due to an unknown error.",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ConfirmResetPasswordView(APIView):
    """ """

    permission_classes = [AllowAny]
    serializer_class = ConfirmResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        """
        POST method for email activation
        """
        try:
            # get token , email, password
            email = request.data.get("email", False)
            token = request.data.get("token", False)
            password = request.data.get("password", False)

            if email and token and password:

                try:
                    user_to_reset = DbExistenceChecker().check_return_user_existence(
                        email=email
                    )
                except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                    raise NoneExistenceError(
                        "User",
                        create_400(
                            400,
                            "Non existence",
                            "User associated to token does not exist",
                        ),
                    )
                try:
                    email_token = DbExistenceChecker().check_return_token_existence(
                        token=token
                    )
                except (TypeError, ValueError, OverflowError, EmailToken.DoesNotExist):
                    raise NoneExistenceError(
                        "Email Token",
                        create_400(
                            400,
                            "Non existence",
                            "Token does not exist",
                        ),
                    )

                # check expired
                if email_token.check_expired:
                    raise ExpiredError(
                        "Email Token",
                        create_400(
                            400, "Expired", "Email Token already expired or used!"
                        ),
                    )

                # check token user and uid match
                if email_token.user.id != user_to_reset.id:
                    raise UnmatchedFieldsError(
                        "User",
                        create_400(
                            400, "Not matching", "Url user and Token user don't match!"
                        ),
                    )

                user_to_reset.set_password(password)
                user_to_reset.save()

                email_token.expired = True
                email_token.save()

                return Response(
                    create_200(
                        200,
                        "Password Resetted!",
                        "Password has been resetted. Now you can login to your account",
                    )
                )
            else:
                raise MissingFieldsError(
                    instance=request,
                    message=create_400(
                        status.HTTP_400_BAD_REQUEST,
                        "Missing fields",
                        "Either of the required fileds: email, password, and/or token missing",
                    ),
                )
        except (MissingFieldsError, NoneExistenceError, ExpiredError) as error:
            return Response(error.message, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response(
                create_500(
                    verbose=f"Could not reset password due to an unknown error.",
                    cause=error.args[0] or None,
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
