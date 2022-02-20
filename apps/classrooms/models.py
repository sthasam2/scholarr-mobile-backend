from django.db import models

from apps.classroom_contents.models import Classwork, Resource
from apps.schedules.models import Schedule
from apps.users.models import CustomUser


class Classroom(models.Model):
    """Modelling a classroom with a teacher and their students"""

    _created_by = models.ForeignKey(
        to=CustomUser, on_delete=models.CASCADE, related_name="created_classroom"
    )
    _created_date = models.DateTimeField(auto_now_add=True)
    _modified_date = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    classroom_code = models.CharField(max_length=32)

    archive = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Classrooms"

    def __str__(self) -> str:
        return f"{self.name} by {self._created_by}"


#########################
#   RELATIONSHIPS
#########################

# Custom User Relationships


class ClassroomHasTeacher(models.Model):
    """Realtion between Classroom and Teacher"""

    classroom = models.ForeignKey(
        to=Classroom, on_delete=models.CASCADE, related_name="classroom_teacher"
    )
    teacher = models.ForeignKey(
        to=CustomUser, on_delete=models.CASCADE, related_name="teacher_classroom"
    )


class ClassroomHasStudent(models.Model):
    """Realtion between Classroom and Student"""

    classroom = models.ForeignKey(
        to=Classroom, on_delete=models.CASCADE, related_name="classroom_student"
    )
    student = models.ForeignKey(
        to=CustomUser, on_delete=models.CASCADE, related_name="student_classroom"
    )


# Classwork/ Content Relationships


class ClassroomHasClasswork(models.Model):
    """Realtion between Classroom and Student"""

    classroom = models.ForeignKey(
        to=Classroom, on_delete=models.CASCADE, related_name="classroom_classwork"
    )
    classwork = models.ForeignKey(
        to=Classwork, on_delete=models.CASCADE, related_name="classwork_classroom"
    )


class ClassroomHasResource(models.Model):
    """Realtion between Classroom and Student"""

    classroom = models.ForeignKey(
        to=Classroom, on_delete=models.CASCADE, related_name="classroom_resource"
    )
    resource = models.ForeignKey(
        to=Resource, on_delete=models.CASCADE, related_name="resource_classroom"
    )


# Schedule Relationships


class ClassroomHasSchedule(models.Model):
    """Realtion between Classroom and Student"""

    classroom = models.ForeignKey(
        to=Classroom, on_delete=models.CASCADE, related_name="classroom_schedule"
    )
    schedule = models.ForeignKey(
        to=Schedule, on_delete=models.CASCADE, related_name="schedule_classroom"
    )
