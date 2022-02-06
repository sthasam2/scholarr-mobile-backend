from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.users.models import CustomUser


class UserActivity(models.Model):
    """
    Model for user activities
    """

    class Actions(models.TextChoices):
        # user
        SIGN_UP = "sgu", "signed up"
        LOG_IN = "lgn", "logged in"
        RESET_PW = "rstpw", "reset password"
        DEACTIVATE = "deac", "deactivated"
        DELETE = "del", "deleted"
        # profile
        VIEW = "vw", "viewed"
        UPDATE = "upd", "updated"
        # buzz
        POST = "pst", "posted"
        UPVOTE = "upv", "upvoted"
        DOWNVOTE = "dwv", "downvoted"
        CREATE = "crt", "created"
        COMMENT = "cmt", "commented"
        EDIT = "edt", "edited"
        # follow
        UNFOLLOW = "unflw", "unfollowed"
        FOLLOW = "flw", "followed"
        REQUEST = "req", "requested"

    user = models.ForeignKey(
        CustomUser,
        related_name="activity_of",
        db_index=True,
        on_delete=models.CASCADE,
    )

    action = models.CharField(
        max_length=250, choices=Actions.choices
    )  # the action of the user

    action_content = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name="activity_object",
        on_delete=models.CASCADE,
    )  # the action object
    action_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    target_content = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name="activity_target",
        on_delete=models.CASCADE,
    )  # the target object
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Additional meta info
        """

        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"
        ordering = ("-created_date",)

    def __str__(self):
        """
        default string method when object called
        """
        return f"User:{self.user}  Action: {self.get_action_display()}  Target: {self.target_content}--id:{self.target_id}"
