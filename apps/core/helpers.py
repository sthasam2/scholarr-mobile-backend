##############################
# data manipulation methods
#############################
from apps.core.exceptions import ExtraFieldsError, MissingFieldsError


def create_500(cause=None, verbose=None) -> dict:
    """
    creates a dictionary with error code, type, message
    """
    return {
        "status": 500,
        "error": {
            "cause": cause,
            "type": "Internal Server Error",
            "message": "Could not process request due to an internal server error.",
            "verbose": verbose,
        },
    }


def create_400(status: int, message: str, detail: str, cause: str = None) -> dict:
    """
    creates a dictionary with error code, message, detail
    """
    return {
        "status": status,
        "error": {
            "message": message,
            "detail": detail,
            "cause": cause,
        },
    }


def create_200(status: int, message: str, detail: str, cause: str = None) -> dict:
    """
    creates a dictionary with success code, message, message
    """
    return {
        "status": status,
        "success": {
            "message": message,
            "detail": detail,
            "cause": cause,
        },
    }


class RequestFieldsChecker:
    """ """

    def check_at_least_one_field_or_raise(
        self, req_body: dict, field_options: list
    ) -> None:
        """ """

        included = list()
        for key, value in req_body.items():
            if key in field_options:
                included.append(key)

        if len(included) == 0:
            raise MissingFieldsError(
                message=create_400(
                    400,
                    "Missing Fields",
                    f"No fields from required were provided",
                ),
            )
        else:
            return None

    def check_extra_fields_or_raise(
        self, req_body: dict, field_options: list, required_fields: list = None
    ) -> None:
        """ """

        extra = list()
        for key, value in req_body.items():
            if key not in field_options and key not in required_fields:
                extra.append(key)

        if len(extra) != 0:
            raise ExtraFieldsError(
                message=create_400(
                    400,
                    "Extra Fields",
                    f"Extra fields were provided: \n {extra}",
                ),
            )
        else:
            return None

    def check_required_field_or_raise(self, req_body, required_fields: list) -> None:
        """ """

        included = list()
        for key, value in req_body.items():
            if key in required_fields:
                included.append(key)

        missing = set(required_fields) - set(included)

        if len(missing) != 0:
            raise MissingFieldsError(
                missing,
                create_400(
                    400,
                    "Missing Fields",
                    f"The following required fields are missing:\n {missing}",
                ),
            )
        else:
            return None

    def check_fields(self, req_data=None, field_options=None, required_fields=None):
        """ """

        if required_fields is not None:
            RequestFieldsChecker().check_required_field_or_raise(
                req_data, required_fields
            )

        if field_options is not None:
            RequestFieldsChecker().check_at_least_one_field_or_raise(
                req_data, field_options
            )

        if required_fields is not None and field_options is not None:
            RequestFieldsChecker().check_extra_fields_or_raise(
                req_data, field_options, required_fields
            )
