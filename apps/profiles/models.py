from django.core.validators import RegexValidator
from django.db import models

from apps.users.models import CustomUser

from .validators import validate_date_lt_today


class Profile(models.Model):
    """ """

    user = models.OneToOneField(
        CustomUser, related_name="user_profile", on_delete=models.CASCADE
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    account_verified = models.BooleanField(default=False)

    use_persona = models.BooleanField(default=True)

    persona = models.PositiveIntegerField(default=1)
    avatar = models.ImageField(default="default.png", upload_to="avatar/")
    cover = models.ImageField(default="default.png", upload_to="cover/")

    bio = models.CharField(
        max_length=200, help_text="What's on your mind?", null=True, blank=True
    )
    name = models.CharField(
        max_length=747,
        unique=False,
        help_text="Full Name. For eg. Will Smith ",
    )
    nickname = models.CharField(
        max_length=50,
        unique=False,
        help_text="Nickname. The name you want to be called. For eg. Will",
    )
    dob = models.DateTimeField(
        validators=[validate_date_lt_today],
        null=True,
        unique=False,
        blank=True,
    )
    location = models.CharField(
        max_length=200,
        help_text="User Location. Street, Municipality/VDC, State, Country",
        null=True,
        blank=True,
    )

    phone_validator = RegexValidator(
        regex=r"^\+?1?\d{9,14}$",
        message="Phone number. It must contain Dialing code and contact number. For eg. +977980000000000",
    )
    phone = models.CharField(
        validators=[phone_validator],
        max_length=17,
        unique=True,
        blank=True,
        null=True,
    )
    phone_verified = models.BooleanField(
        help_text="Contact number verified", default=False
    )

    private = models.BooleanField(help_text="Profile Privacy", default=False)

    def __str__(self):
        return f"{self.user.username} Profile"

    def get_username(self):
        return self.user.username
