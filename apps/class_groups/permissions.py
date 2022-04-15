from rest_framework.permissions import BasePermission

from apps.class_groups.models import ClassGroup


class IsClassGroupOwner(BasePermission):
    """ """

    def has_object_permission(self, request, view, obj: ClassGroup):
        """ """

        return obj._created_by == request.user
