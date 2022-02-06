from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


from apps.profiles.models import Profile
from apps.users.models import CustomUser

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
