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
    instance: given instance which caused error
    message: message for given error

    """

    name = None

    def __init__(self, instance=None, message=None, summary=None):
        self.name = type(self).__name__
        self.instance = instance
        self.message = message
        self.summary = summary

    def __str__(self):
        return f"""
        {self.name}:
        \n\tcause: {self.instance} 
        \n\summary: {self.summary}
        \n\tmessage: {self.message}
        """

    class Meta:
        abstract = True


class RequestBodyError(CustomBaseError):
    """
    Exception raise when request body doesn't have fields
    """


class MissingFieldsError(CustomBaseError):
    """
    Exception raised when fields are missing
    """

    pass


class UnknownModelFieldsError(CustomBaseError):
    """
    Exception raised when model fields dont exist
    """

    pass


class PreviousValueMatchingError(CustomBaseError):
    """
    Exception raised when model fields dont exist
    """

    pass


class ExtraFieldsError(CustomBaseError):
    """
    Exception raised when fields are extra than required
    """

    pass


class UrlParameterError(CustomBaseError):
    """
    Exception raised when url parameter is wrong
    """

    pass


class PreExistenceError(CustomBaseError):
    """
    Exception raised when a value already exists somewhere
    """

    pass


class NoneExistenceError(CustomBaseError):
    """
    Exception raised when a value already doesnt exists
    """

    pass


class UnmatchedFieldsError(CustomBaseError):
    """
    Exception raised when a value already exists somewhere
    """

    pass


class AlreadyEmailVerifiedError(CustomBaseError):
    """
    Exception raised when a user has not verified his email
    """

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


class SelfReferenceError(CustomBaseError):
    """
    Exception raised when a ownself is refernced for certain tasks
    """

    pass


class PermissionDeniedError(PermissionDenied):
    """ """

    pass


class NotAuthenticatedError(NotAuthenticated):
    """ """

    pass


class CustomAuthenticationFailed(CustomBaseError):
    """ """

    pass
