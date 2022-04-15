"""
Custom Exceptions
"""
from rest_framework.exceptions import NotAuthenticated, PermissionDenied


class Error(Exception):
    """
    Common base for all exceptions @Error
    """

    pass


class CustomBaseError(Error):
    """
    Base for customized errors

    Parameters
    ---
    cause: given instance which caused error
    message: message for given error

    """

    name = None

    def __init__(self, cause=None, verbose=None, message=None, status_code=None):
        self.name = type(self).__name__
        self.cause = cause
        self.verbose = verbose
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f"""
        {self.name}:
        \n\tcause: {self.cause} 
        \n\tmessage: {self.message}
        \n\tverbose: {self.verbose}
        \n\tstatus: {self.status_code}
        """

    class Meta:
        abstract = True


class AlreadyEmailVerifiedError(CustomBaseError):
    """
    Exception raised when a user has not verified his email
    """

    pass


class AlreadyInvitedError(CustomBaseError):
    """
    Exception raised when a user has already been invited
    """

    pass


class AlreadyMemberError(CustomBaseError):
    """
    Exception raised when a user is already member
    """

    pass


class AlreadyRespondedError(CustomBaseError):
    """
    Exception raised when a user has already accepted or rejected i.e. responded
    """

    pass


class AlreadyRequestedError(CustomBaseError):
    """
    Exception raised when a user has already made request
    """

    pass


class AlreadyTeacherError(CustomBaseError):
    """
    Exception raised when a user is already teacher
    """

    pass


class CustomAuthenticationFailed(CustomBaseError):
    """ """

    pass


class EmailNotVerifiedError(CustomBaseError):
    """
    Exception raised when a user has not verified his email
    """

    pass


class ExpiredError(CustomBaseError):
    """
    Exception raised when a token is expired
    """

    pass


class ExtraFieldsError(CustomBaseError):
    """
    Exception raised when fields are extra than required
    """

    pass


class LimitExceededError(CustomBaseError):
    """
    Exception raised when limits are exceeded in fields
    """

    pass


class MissingFieldsError(CustomBaseError):
    """
    Exception raised when fields are missing
    """

    pass


class MultipleInstancesError(CustomBaseError):
    """Error when multiple instances are obtained when only one instance is required"""

    pass


class NoneExistenceError(CustomBaseError):
    """
    Exception raised when a value already doesnt exists
    """

    pass


class NotAuthenticatedError(NotAuthenticated):
    """ """

    pass


class PermissionDeniedError(PermissionDenied):
    """ """

    pass


class PreExistenceError(CustomBaseError):
    """
    Exception raised when a value already exists somewhere
    """

    pass


class PreviousValueMatchingError(CustomBaseError):
    """
    Exception raised when model fields dont exist
    """

    pass


class RequestBodyError(CustomBaseError):
    """
    Exception raise when request body doesn't have fields
    """


class SelfReferenceError(CustomBaseError):
    """
    Exception raised when a ownself is refernced for certain tasks
    """

    pass


class UnknownModelFieldsError(CustomBaseError):
    """
    Exception raised when model fields dont exist
    """

    pass


class UnmatchedFieldsError(CustomBaseError):
    """
    Exception raised when a value already exists somewhere
    """

    pass


class UrlParameterError(CustomBaseError):
    """
    Exception raised when url parameter is wrong
    """

    pass
