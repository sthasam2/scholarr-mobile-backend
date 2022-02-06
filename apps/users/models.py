import datetime as dt

import pytz
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser):
    """
    Custom extension of the AbstractBaseUser to create a custom user field
    """

    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        help_text="Username. example: sam_smith",
    )
    email = models.EmailField(
        max_length=150,
        unique=True,
        db_index=True,
        help_text="Email address. example: example@example.domain",
    )

    registered_date = models.DateTimeField(auto_now_add=True)
    email_verified = models.BooleanField(default=False)

    admin = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Custom User"
        verbose_name_plural = "Custom Users"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_superuser(self):
        return self.admin

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_active(self):
        return self.active

    @property
    def is_email_verified(self):
        return self.email_verified


class EmailToken(models.Model):
    """
    A token for email verification
    """

    class Purpose(models.TextChoices):
        """
        Choices for Token creation purpose
        """

        EMAIL_VERIFICATION = "e_ver", "Email Verification"
        PASSWORD_RESET = "p_rst", "Password Reset"
        ACTIVATE_ACCOUNT = "act_acc", "Activate Account"

    purpose = models.CharField(max_length=50, choices=Purpose.choices)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)
    used = models.BooleanField(default=False)

    def __str__(self):
        return self.token

    @property
    def check_expired(self, *args, **kwargs):
        """
        Check expired email
        """
        td = pytz.timezone("UTC").localize(dt.datetime.utcnow()) - self.created_date
        if td.total_seconds() > (15 * 60):
            self.expired = True
            super().save(*args, **kwargs)

        return self.expired
