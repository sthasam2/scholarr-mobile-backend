from django.db.models import Q
from rest_framework.permissions import BasePermission

from apps.classrooms.models import (
    Classroom,
    ClassroomHasStudent,
    ClassroomHasTeacher,
    ClassroomInviteOrRequest,
)


class IsClassroomMember(BasePermission):
    """ """

    def has_object_permission(self, request, view, obj: Classroom):
        """ """

        assert isinstance(obj, Classroom)

        is_teacher = ClassroomHasTeacher.objects.filter(
            Q(classroom=obj.id) & Q(teacher=request.user)
        ).exists()
        is_student = ClassroomHasStudent.objects.filter(
            Q(classroom=obj.id) & Q(student=request.user)
        ).exists()

        return is_student or is_teacher


class IsClassroomOwner(BasePermission):
    """ """

    def has_object_permission(self, request, view, obj: Classroom):
        """ """
        assert isinstance(obj, Classroom)

        return obj._created_by == request.user


class IsClassroomOwnerOrTeacher(BasePermission):
    """ """

    def has_object_permission(self, request, view, obj: Classroom):
        """ """

        assert isinstance(obj, Classroom)

        return obj._created_by == request.user or obj.classroom_teacher == request.user


class IsClassroomInviteCreatorOrTarget(BasePermission):
    """ """

    def has_object_permission(self, request, view, obj: ClassroomInviteOrRequest):
        """ """

        assert isinstance(obj, ClassroomInviteOrRequest)

        return (
            obj._created_by == request.user
            or obj.student == request.user
            or obj.teacher == request.user
        )
