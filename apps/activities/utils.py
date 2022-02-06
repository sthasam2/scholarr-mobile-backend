from .models import UserActivity


def _create_activity(
    user: object,
    action: str,
    action_content: object = None,
    action_id: int = None,
    target_content: object = None,
    target_id: int = None,
    *args,
    **kwargs
):
    """
    Creates activity based on certain actions by the user

    Params
    ---
    user(object):
    action(str):
    action_content(object)
    action_id(int)
    target_content()
    target_id(int)
    """

    activity = UserActivity(
        user=user,
        action=action,
        action_content=action_content,
        action_id=action_id,
        target_content=target_content,
        target_id=target_id,
    )
    activity.save()


# TODO add checks for previous activity, spammy behaviour etc
