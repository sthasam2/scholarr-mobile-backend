from rest_framework import status

from apps.core.exceptions import (
    MissingFieldsError,
    NoneExistenceError,
    UrlParameterError,
)
from apps.core.helpers import RequestFieldsChecker, create_400

from .models import Profile


def get_profile_from_url_username_or_raise(**kwargs):
    """ """

    url_username = kwargs.get("username")
    if url_username:
        try:
            return Profile.objects.get(user__username=url_username)

        except (TypeError, ValueError, OverflowError, Profile.DoesNotExist):
            raise NoneExistenceError(
                url_username,
                create_400(
                    400,
                    "Non existence",
                    f"Account with username {url_username} credentials does not exist!",
                ),
            )
    else:
        raise UrlParameterError(
            instance="Url username",
            message=create_400(
                status.HTTP_400_BAD_REQUEST,
                "Url parameter wrong",
                '"username" must be provided',
            ),
        )


def check_fields(req_data, field_options=None, required_fields=None):
    """ """

    if required_fields is not None:
        if len(required_fields) != 0:
            RequestFieldsChecker().check_required_field_or_raise(
                req_data, required_fields
            )

    if field_options is not None:
        if len(field_options) != 0:
            RequestFieldsChecker().check_at_least_one_field_or_raise(
                req_data, field_options
            )

    if required_fields is not None and field_options is not None:
        if req_data.__len__() == 0:
            raise MissingFieldsError(
                "No fields provided",
                create_400(
                    400,
                    "Missing Fields",
                    f"No fields were provided",
                ),
            )

        RequestFieldsChecker().check_extra_fields_or_raise(
            req_data, field_options, required_fields
        )
