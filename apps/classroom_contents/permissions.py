from rest_framework.permissions import BasePermission

from apps.classroom_contents.models import ClassworkHasSubmission, Submission
from apps.classrooms.models import ClassroomHasClasswork, ClassroomHasTeacher


class IsSubmissionOwner(BasePermission):
    """ """

    def has_object_permission(self, request, view, obj: Submission):
        """ """

        return request.user == obj._created_by


class IsSubmissionOwnerOrClassroomOwnerOrTeacher(BasePermission):
    """ """

    def has_object_permission(self, request, view, obj: Submission):
        """ """

        requesting_user = request.user

        submission_classwork = ClassworkHasSubmission.objects.get(
            submission=obj
        ).classwork

        classwork_classroom = ClassroomHasClasswork.objects.get(
            classwork=submission_classwork
        )

        classroom_teachers = [
            relation.teacher
            for relation in ClassroomHasTeacher.objects.filter(
                classroom=classwork_classroom
            )
        ]

        return (
            requesting_user == obj._created_by
            or requesting_user == classwork_classroom._created_by
            or requesting_user in classroom_teachers
        )
