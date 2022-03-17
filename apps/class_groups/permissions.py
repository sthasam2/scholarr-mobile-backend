from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import BasePermission

from apps.class_groups.models import ClassGroup
from apps.core.helpers import create_400


class IsClassGroupOwner(BasePermission):
    """ """

    def has_object_permission(self, request, view, obj: ClassGroup):
        """ """

        return obj._created_by == request.user
