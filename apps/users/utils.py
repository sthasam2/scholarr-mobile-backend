from random import choice
from string import ascii_lowercase

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from configs.definitions import DEBUG

from .models import CustomUser, EmailToken

#################
# string methods
#################


class TokenGenerator:
    def random_string(self) -> str:
        """
        generates random string
        """
        return "".join(
            choice(ascii_lowercase) for i in range(5)
        )  # choice chooses random from ascii_lowercase for range times and join joins them with "" string

    def token_generator(self) -> str:
        """
        Generates token using django's inbuilt token generator
        """
        return f"{self.random_string()}-{self.random_string()}-{self.random_string()}"

    def create_email_token(self, user, purpose):
        """
        Create an email token
        """
        new_token = EmailToken.objects.create(
            user=user, token=self.token_generator(), purpose=purpose
        )

        return new_token


######################
# DB methods
######################


class DbExistenceChecker:
    """ """

    def check_username_existence(self, username: str) -> bool:
        """
        Checks whether any user with given username exists and returns true or false
        """
        return CustomUser.objects.filter(username=username).exists()

    def check_email_existence(self, email: str) -> bool:
        """
        Checks whether any user with given username exists and returns true or false
        """
        return CustomUser.objects.filter(email=email).exists()

    def check_token_existence(self, user, token: str) -> bool:
        """
        Checks whether any user with given username exists and returns true or false
        """

        return EmailToken.objects.filter(token=token).exists()

    def check_return_user_existence(self, *args, **kwargs) -> bool:
        """
        Checks whether any user with given username exists and returns true or false
        """
        return CustomUser.objects.get(**kwargs)

    def check_return_token_existence(self, token: str, *args, **kwargs) -> bool:
        """
        Checks whether any user with given username exists and returns true or false
        """
        return EmailToken.objects.get(token=token)


#######################
# Network methods
#######################


class EmailSender:
    """ """

    def send_email_verification_mail(self, request, user):
        """
        Sends email validation mail to user with token
        """
        try:
            token = TokenGenerator().create_email_token(
                user=user, purpose=EmailToken.Purpose.EMAIL_VERIFICATION
            )
            context = {
                "user": user,
                "domain": get_current_site(request).domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": token.token,
            }

            message = render_to_string("users/email_verification.html", context)

            mail_response = send_mail(
                subject="[Scholarr-Mobile] Account Email Verification",
                from_email="Scholarr-Mobile Team",
                message="Email verification",
                html_message=message,
                recipient_list=[user.email],
            )

        except Exception as e:
            if DEBUG:
                print(e)

    def send_password_reset_email(self, request, user):
        """
        Sends email for resseting password
        """
        try:
            token = TokenGenerator()

            context = {
                "user": user,
                # "domain": get_current_site(request).domain,
                # "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": token.create_email_token(
                    user=user, purpose=EmailToken.Purpose.PASSWORD_RESET
                ),
            }

            message = render_to_string("users/password_reset.html", context)

            email = send_mail(
                subject="[Scholarr-Mobile] Account Password Reset",
                from_email="Scholarr-Mobile Team",
                message="Reset Password",
                html_message=message,
                recipient_list=[user.email],
            )

        except Exception as e:
            if DEBUG:
                print("Error @ send_password_reset_email()", e)


# TODO add logic
