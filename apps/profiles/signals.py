from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.activities.models import UserActivity
from apps.activities.utils import _create_activity
from configs.definitions import DEBUG

from .models import Profile


@receiver(post_save, sender=Profile)
def profile_post_save(sender, instance, created, **kwargs):
    """
    Reciever function for Profile model post save
    """

    if DEBUG:
        print("Profile `post_save` signal received!")

    if created:
        _create_activity(
            instance.user,
            UserActivity.Actions.UPDATE,
            ContentType.objects.get_for_model(instance),
            instance.id,
        )

        # FIXME check update
