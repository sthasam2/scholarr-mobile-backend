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
            "message": "Could not process request due to an internal server error.",
            "verbose": verbose,
        },
    }


def create_400(status: int, message: str, verbose: str, cause=None) -> dict:
    """
    creates a dictionary with error code, message, verbose
    """
    return {
        "status": status,
        "error": {
            "message": message,
            "verbose": verbose,
            "cause": cause,
        },
    }


def create_200(status: int, message: str, verbose: str, cause=None) -> dict:
    """
    creates a dictionary with success code, message, message
    """
    return {
        "status": status,
        "success": {
            "message": message,
            "verbose": verbose,
            "cause": cause,
        },
    }


class RequestFieldsChecker:
    """ """

    def check_at_least_one_field_or_raise(
        self, req_body: dict, field_options: list
    ) -> None:
        """ """

        included = set(field_options).intersection(set(req_body))
        if len(included) == 0:

            raise MissingFieldsError(
                status_code=400,
                message="Missing Fields",
                verbose=f"No fields from required were provided",
            )
        else:
            return None

    def check_extra_fields_or_raise(
        self, req_body: dict, field_options: list, required_fields: list = None
    ) -> None:
        """ """
        options = set(required_fields).union(set(field_options))
        extra = set(req_body).difference(options)
        if len(extra) != 0:
            raise ExtraFieldsError(
                status_code=400,
                message="Extra Fields",
                verbose=f"Extra fields were provided: \n {extra}",
            )
        else:
            return None

    def check_required_field_or_raise(self, req_body, required_fields: list) -> None:
        """ """

        missing = set(required_fields).difference(set(req_body))

        if len(missing) != 0:
            raise MissingFieldsError(
                status_code=400,
                message="Missing Fields",
                verbose=f"The following required fields are missing:\n {missing}",
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
