from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .api.views.auth_views import (
    ConfirmResetPasswordView,
    LoginView,
    LogoutView,
    RegisterView,
    ResendEmailVerificationView,
    SendResetPasswordView,
    VerifyEmailView,
)
from .api.views.user_views import (
    ActivateUserView,
    ChangePasswordView,
    DeactivateUserView,
    DeleteUserView,
    UpdateUserView,
    UserDetailView,
)

register = [
    path("register/", RegisterView.as_view(), name="register-user"),
]

logins = [
    path("login", LoginView.as_view(), name="login"),
    path("login/refresh", TokenRefreshView.as_view(), name="login-token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

email_verifications = [
    path(
        "email_verification/send",
        ResendEmailVerificationView.as_view(),
        name="send-email-verification",
    ),
    path(
        "email_verification/confirm/<slug:uidb64>/<slug:token>",
        VerifyEmailView.as_view(),
        name="confirm-email-verification",
    ),
]

password_resets = [
    path(
        "reset_password/send",
        SendResetPasswordView.as_view(),
        name="send-password-reset",
    ),
    path(
        "reset_password/confirm",
        ConfirmResetPasswordView.as_view(),
        name="confirm-password-reset",
    ),
]

user_methods = [
    path("user/detail/<slug:username>", UserDetailView.as_view(), name="user-detail"),
    path("user/update/<slug:username>", UpdateUserView.as_view(), name="update-user"),
    path(
        "user/change_password/<slug:username>",
        ChangePasswordView.as_view(),
        name="change-password-user",
    ),
    path(
        "user/deactivate/<slug:username>",
        DeactivateUserView.as_view(),
        name="deactivate-user",
    ),
    path(
        "user/activate",
        ActivateUserView.as_view(),
        name="activate-user",
    ),
    path("user/delete/<slug:username>", DeleteUserView.as_view(), name="delete-user"),
]

urlpatterns = register + logins + email_verifications + password_resets + user_methods
