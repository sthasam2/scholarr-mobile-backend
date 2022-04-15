from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.classrooms.api.serializers import ClassroomSerializer
from apps.classrooms.models import ClassroomHasSchedule
from apps.classrooms.permissions import IsClassroomOwnerOrTeacher
from apps.classrooms.utils import get_url_id_classroom_or_raise
from apps.core.decorators import try_except_http_error_decorator
from apps.core.helpers import create_200
from apps.core.permissions import IsAuthenticatedCustom
from apps.schedules.api.serializers import (
    CreateScheduleSerializer,
    ReadScheduleSerializer,
    ScheduleClassroomSerializer,
    UpdateScheduleSerializer,
)
from apps.schedules.models import Schedule
from apps.schedules.utils import get_url_id_schedule_or_raise


class ScheduleViewset(ViewSet):
    """ """

    serializer_class = ReadScheduleSerializer
    read_serializer_class = ReadScheduleSerializer
    create_serializer_class = CreateScheduleSerializer
    update_serializer_class = UpdateScheduleSerializer
    classroom_serializer = ScheduleClassroomSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticatedCustom]

        if self.action in ["create", "update", "delete"]:
            permission_classes.append(IsClassroomOwnerOrTeacher)

        return [permission() for permission in permission_classes]

    @extend_schema(request=create_serializer_class)
    @try_except_http_error_decorator
    def create(self, *args, **kwargs):
        """ """

        url_classroom_id = kwargs.get("classroom_id")

        if url_classroom_id:
            classroom_instance = get_url_id_classroom_or_raise(url_classroom_id)
            self.check_object_permissions(self.request, classroom_instance)

            serializer = self.create_serializer_class(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            created_schedule = serializer.save(_created_by=self.request.user)

            ClassroomHasSchedule.objects.create(
                classroom=classroom_instance,
                schedule=created_schedule,
            )

            return Response(
                data=create_200(
                    201,
                    "Created Schedule",
                    "Schedule has been created for given classroom",
                    serializer.validated_data,
                ),
                status=201,
            )

    @try_except_http_error_decorator
    def list(self, *args, **kwargs):
        """ """

        url_classroom_id = kwargs.get("classroom_id")

        if url_classroom_id:
            classroom_instance = get_url_id_classroom_or_raise(url_classroom_id)

            classroom_schedules = [
                classroom_has_schedule.schedule
                for classroom_has_schedule in classroom_instance.classroom_schedule.all()
            ]

            schedule_serializer = self.read_serializer_class(
                classroom_schedules, many=True
            )
            classroom_serializer = self.classroom_serializer(classroom_instance)

            return Response(
                data=dict(
                    schedules=schedule_serializer.data,
                    classroom=classroom_serializer.data,
                ),
                status=200,
            )

    @try_except_http_error_decorator
    def self_list(self, *args, **kwargs):
        """ """

        studying_classroom = [
            classroom_has_student.classroom
            for classroom_has_student in self.request.user.student_classroom.all()
        ]
        teaching_classroom = [
            classroom_has_teacher.classroom
            for classroom_has_teacher in self.request.user.teacher_classroom.all()
        ]

        studying_schedules = [
            classroom_has_schedule.schedule
            for classroom_has_schedule in ClassroomHasSchedule.object.filter(
                classroom_in=studying_classroom
            ).all()
        ]
        teaching_schedules = [
            classroom_has_schedule.schedule
            for classroom_has_schedule in ClassroomHasSchedule.object.filter(
                classroom_in=teaching_classroom
            ).all()
        ]

        studying_schedule_serializer = self.read_serializer_class(
            Schedule.objects.filter(id__in=studying_schedules), many=True
        )
        teaching_schedule_serializer = self.read_serializer_class(
            Schedule.objects.filter(id__in=teaching_schedules), many=True
        )

        return Response(
            data=dict(
                studying=studying_schedule_serializer.data,
                teaching=teaching_schedule_serializer.data,
            ),
            status=200,
        )

    @try_except_http_error_decorator
    def detail_schedule(self, *args, **kwargs):
        """ """

        url_schedule_id = kwargs.get("schedule_id", None)

        if url_schedule_id:
            schedule_instance = get_url_id_schedule_or_raise(url_schedule_id)
            serializer = self.read_serializer_class(schedule_instance)

            class_serializer = self.classroom_serializer(
                schedule_instance.schedule_classroom.get().classroom
            )

            return Response(
                data=dict(schedule=serializer.data, classroom=class_serializer.data),
                status=200,
            )

    @extend_schema(request=update_serializer_class)
    @try_except_http_error_decorator
    def update(self, *args, **kwargs):
        """ """

        url_schedule_id = kwargs.get("schedule_id", None)

        if url_schedule_id:
            schedule_instance = get_url_id_schedule_or_raise(url_schedule_id)
            schedule_classroom = schedule_instance.schedule_classroom.get().classroom

            self.check_object_permissions(self.request, schedule_classroom)

            serializer = self.update_serializer_class(
                schedule_instance, data=self.request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                data=create_200(
                    201,
                    "Updated Schedule",
                    "Schedule has been updated",
                    cause=serializer.validated_data,
                ),
                status=201,
            )

    @try_except_http_error_decorator
    def delete(self, *args, **kwargs):
        """ """

        url_schedule_id = kwargs.get("schedule_id", None)

        if url_schedule_id:
            schedule_instance = get_url_id_schedule_or_raise(url_schedule_id)
            schedule_classroom = schedule_instance.schedule_classroom.get().classroom

            self.check_object_permissions(self.request, schedule_classroom)

            schedule_instance.delete()

            return Response(
                data=create_200(
                    204,
                    "Deleted Schedule",
                    "Schedule has been deleted",
                ),
                status=204,
            )
