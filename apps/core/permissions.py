from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import BasePermission

from apps.core.helpers import create_400
from apps.profiles.models import Profile
from apps.users.models import CustomUser


class IsAuthenticatedCustom(BasePermission):
    """Custom IsAuthenticated Permission"""

    def has_permission(self, request, view):

        is_authenticated = bool(request.user and request.user.is_authenticated)
        if is_authenticated:
            return is_authenticated
        else:
            raise NotAuthenticated(
                create_400(
                    status=401,
                    cause=request,
                    message="Not Authenticated",
                    verbose="Authentication credentials were not provided.",
                )
            )


######################################
##           OWNER
######################################


class IsOwner(BasePermission):
    """ """

    def has_object_permission(self, request, view, obj: CustomUser):
        """ """

        is_owner = obj == request.user
        if is_owner:
            return is_owner
        else:
            raise PermissionDenied(
                detail="Request user is not an instance of Targeted user. Permission Denied",
                code="Permission Denied!",
            )


class IsProfileOwner(BasePermission):
    """ """

    def has_object_permission(self, request, view, obj: Profile):
        """ """

        return obj.user == request.user


######################################
##           PRIVACY
######################################


class IsProfilePrivate(BasePermission):
    """ """

    def has_object_permission(self, request, view, obj):
        """ """

        return obj.private == True


######################################
##           MATCHING
######################################


class IsPasswordMatching(BasePermission):
    """ """

    def has_object_permission(self, request, view, obj: CustomUser):
        """ """

        password_matching = obj.check_password(request.data.get("current_password"))
        if password_matching:
            return password_matching
        else:
            raise PermissionDenied(
                detail="Password incorrect. Please enter correct password",
                code="Permission Denied!",
            )


class IsProfilePasswordMatching(BasePermission):
    """ """

    def has_object_permission(self, request, view, obj: Profile):
        """ """

        return obj.user.check_password(request.data.get("current_password"))
