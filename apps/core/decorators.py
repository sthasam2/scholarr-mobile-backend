from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
)
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .exceptions import *
from .helpers import create_200, create_400, create_500


def try_except_http_error_decorator(func, *args, **kwargs):
    """Decorator for try catch block"""

    def http_inner(*args, **kwargs):
        """execution  of inner function"""

        try:
            returned_value = func(*args, **kwargs)
            return returned_value

        # 400: Bad Request, No resource
        except (
            AlreadyEmailVerifiedError,
            ExpiredError,
            ExtraFieldsError,
            MissingFieldsError,
            NoneExistenceError,
            PreExistenceError,
            UrlParameterError,
            UnmatchedFieldsError,
        ) as error:
            return Response(
                create_400(
                    status=error.status_code or 400,
                    message=error.message or None,
                    verbose=error.verbose or None,
                    cause=error.cause or None,
                ),
                status=error.status_code,
            )

        # 401: Unauthorized/ Forbidden
        except (PermissionDenied, NotAuthenticated, AuthenticationFailed) as error:
            return Response(
                create_400(
                    status=error.status_code,
                    message=error.get_codes(),
                    verbose=error.get_full_details().get("message"),
                ),
                status=error.status_code,
            )

        # 401: Access Denied
        except TokenError as e:
            raise InvalidToken(e.args[0])

        except CustomAuthenticationFailed as error:
            return Response(
                create_400(
                    status=error.status_code or 400,
                    message=error.message or None,
                    verbose=error.verbose or None,
                    cause=error.cause or None,
                ),
                status=error.status_code,
            )

        # 500: Server Error
        except Exception as error:
            return Response(
                create_500(
                    verbose=error.args[0] or None,
                    cause=error.default_detail,
                ),
                status=500,
            )

    return http_inner
