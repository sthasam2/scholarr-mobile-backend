from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.decorators import try_except_http_error_decorator
from apps.core.exceptions import (
    AlreadyEmailVerifiedError,
    ExpiredError,
    MissingFieldsError,
    NoneExistenceError,
    PreExistenceError,
    UnmatchedFieldsError,
)
from apps.core.helpers import create_200
from apps.core.permissions import IsAuthenticatedCustom
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

    @try_except_http_error_decorator
    def post(self, request, *args, **kwargs):
        """
        Register POST method
        """

        email = request.data.get("email", False)
        username = request.data.get("username", False)
        password = request.data.get("password", False)

        if email and username and password:

            if DbExistenceChecker().check_email_existence(email):
                raise PreExistenceError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Duplicate",
                    verbose=f'User with email "{email}" already exists. Try a different email',
                    cause="@Register post: email",
                )

            if DbExistenceChecker().check_username_existence(username):
                raise PreExistenceError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Already exists",
                    verbose=f'User with username "{username}" already exists. Try a different username',
                    cause="@Register post: username",
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
                    f"Account with email `{email}` and username `{username}` created!\nPlease verify email to login.",
                ),
                status=status.HTTP_201_CREATED,
            )
        else:
            raise MissingFieldsError(
                status_code=400,
                message="Missing Fields",
                verbose="Either of the required fields email, username, and/or password is missing.",
                cause="Register post",
            )


##################################
##          RETRIEVE
##################################


class ResendEmailVerificationView(APIView):
    """ """

    permission_classes = [AllowAny]
    serializer_class = SendEmailVerificationSerializer

    @try_except_http_error_decorator
    def post(self, request, *args, **kwargs):
        """ """

        # TODO  check last sent verification and dont allow multiple email in certain timeframe

        email = request.data.get("email", False)
        if email:
            try:
                user_requested = DbExistenceChecker().check_return_user_existence(
                    email=email
                )
            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                raise NoneExistenceError(
                    status_code=400,
                    message="Non existence",
                    verbose=f"Account with email {email} credentials does not exist! Check email or sign up using a different email",
                    cause="email",
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
                    status_code=400,
                    message="Already verified",
                    verbose="`email` already verified.",
                    cause="verified",
                )

        else:
            raise MissingFieldsError(
                instance=request,
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Missing fields",
                verbose="`email` field is mandatory. Please provide email",
                cause="reqbody:email",
            )


class LoginView(CustomTokenObtainPairView):
    """ """

    permission_classes = [AllowAny]


class LogoutView(APIView):
    """ """

    permission_classes = [IsAuthenticatedCustom]
    serializer_class = LogoutSerializer

    @try_except_http_error_decorator
    def post(self, request, *args, **kwargs):
        """ """

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
                status_code=400,
                message="Missing Fields",
                verbose="`refresh` must be provided with refresh token",
                cause="reqbody:refresh",
            )


class SendResetPasswordView(APIView):
    """ """

    permission_classes = [AllowAny]
    serializer_class = SendResetPasswordSerializer

    @try_except_http_error_decorator
    def post(self, request, *args, **kwargs):
        """ """

        # TODO  check last sent verification and dont allow multiple email in certain timeframe

        email = request.data.get("email", False)
        if email:
            try:
                user_requested = DbExistenceChecker().check_return_user_existence(
                    email=email
                )
            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                raise NoneExistenceError(
                    status_code=404,
                    message="Non existence",
                    verbose=f"Account with email {email} credentials does not exist!",
                    cause="email",
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
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Missing fields",
                verbose="`email` field is mandatory. Please provide email",
                cause="reqbod:email",
            )


##################################
##          UPDATE
##################################


class VerifyEmailView(APIView):
    """ """

    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    @try_except_http_error_decorator
    def get(self, request, *args, **kwargs):
        """
        GET method for email activation
        """

        # get token and username
        uid = force_str(urlsafe_base64_decode(kwargs["uidb64"]))
        token = kwargs["token"]

        # check token and user existence
        try:
            user_to_verify = DbExistenceChecker().check_return_user_existence(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise NoneExistenceError(
                status_code=404,
                message="Non existence",
                verbose="User associated to token does not exist",
                cause="User",
            )

        try:
            email_token = DbExistenceChecker().check_return_token_existence(token=token)
        except (TypeError, ValueError, OverflowError, EmailToken.DoesNotExist):
            raise NoneExistenceError(
                status_code=400,
                message="Non existence",
                verbose="Token does not exist",
                cause="token",
            )

        # check expired
        if email_token.check_expired:
            raise ExpiredError(
                status_code=400,
                message="Expired",
                verbose="Email Token already expired!",
                cause="token",
            )

        # check token user and uid match
        if email_token.user.id != user_to_verify.id:
            raise UnmatchedFieldsError(
                status_code=400,
                message="Not matching",
                verbose="Url user and Token user don't match!",
                cause="token",
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


class ConfirmResetPasswordView(APIView):
    """ """

    permission_classes = [AllowAny]
    serializer_class = ConfirmResetPasswordSerializer

    @try_except_http_error_decorator
    def post(self, request, *args, **kwargs):
        """
        POST method for email activation
        """

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
                    status_code=400,
                    message="Non existence",
                    verbose="User associated to token does not exist",
                    cause="User",
                )
            try:
                email_token = DbExistenceChecker().check_return_token_existence(
                    token=token
                )
            except (TypeError, ValueError, OverflowError, EmailToken.DoesNotExist):
                raise NoneExistenceError(
                    status_code=400,
                    message="Non existence",
                    verbose="Token does not exist",
                    cause="Token",
                )

            # check expired
            if email_token.check_expired:
                raise ExpiredError(
                    status_code=400,
                    message="Expired",
                    verbose="Email Token already expired or used!",
                    cause="Token",
                )

            # check token user and uid match
            if email_token.user.id != user_to_reset.id:
                raise UnmatchedFieldsError(
                    status_code=400,
                    message="Not matching",
                    verbose="Url user and Token user don't match!",
                    cause="User and Token",
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
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Missing fields",
                verbose="Either of the required fileds: email, password, and/or token missing",
                cause="Req body",
            )
