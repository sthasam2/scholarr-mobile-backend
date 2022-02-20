from configs.definitions import DEBUG
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.activities.models import UserActivity
from apps.activities.utils import _create_activity
from apps.profiles.models import Profile

from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def post_save_create_save_profile_and_activity(sender, instance, created, **kwargs):
    if created:
        if DEBUG:
            print(
                f"`post_save_create_save_profile_and_activity` signal received!",
            )

        # create profile
        profile = Profile.objects.create(user=instance)

        _create_activity(
            user=instance,
            action=UserActivity.Actions.SIGN_UP,
            target_content=ContentType.objects.get_for_model(CustomUser),
            target_id=instance.id,
        )
        # profile
        _create_activity(
            user=instance,
            action=UserActivity.Actions.CREATE,
            target_content=ContentType.objects.get_for_model(Profile),
            target_id=profile.id,
        )


# TODO custom email verified signal
