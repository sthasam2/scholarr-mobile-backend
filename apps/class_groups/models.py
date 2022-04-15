from django.contrib.auth import get_user_model
from django.db import models


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="deleted")[0]


# Create your models here.
class ClassGroup(models.Model):
    """Modelling a class"""

    _created_by = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.SET(get_sentinel_user),
        related_name="created_classgroup",
    )
    _created_date = models.DateTimeField(auto_now_add=True)
    _modified_date = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=200)
    classgroup_code = models.CharField(max_length=32)

    faculty = models.CharField(max_length=200)
    batch = models.CharField(max_length=200)
    organisation = models.CharField(max_length=200)

    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "ClassGroups"

    def __str__(self) -> str:
        return f"{self.name}(id={self.id})"


############################
#   RELATIONSHIPS
############################


class ClassGroupHasClassroom(models.Model):
    """"""

    classgroup = models.ForeignKey(
        to=ClassGroup,
        on_delete=models.CASCADE,
        related_name="classgroup_classroom",
    )
    classroom = models.ForeignKey(
        to="classrooms.Classroom",
        on_delete=models.CASCADE,
        related_name="classroom_classgroup",
    )

    class Meta:
        verbose_name_plural = "Classgroup Classrooms"

    def __str__(self) -> str:
        return f"{self.classgroup} has classroom {self.classroom}"


class ClassGroupHasStudent(models.Model):
    """"""

    classgroup = models.ForeignKey(
        to=ClassGroup,
        on_delete=models.CASCADE,
        related_name="classgroup_student",
    )
    student = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name="student_classgroup",
    )

    class Meta:
        verbose_name_plural = "Classgroup Students"

    def __str__(self) -> str:
        return f"{self.classgroup} has student {self.student}"


class ClassGroupHasRoutineSchedules(models.Model):
    """"""

    classgroup = models.ForeignKey(
        to=ClassGroup,
        on_delete=models.CASCADE,
        related_name="classgroup_schedule",
    )
    # schedule = models.ForeignKey(
    #     to=,
    #     on_delete=models.CASCADE,
    #     related_name="schedule_classgroup",
    # )

    class Meta:
        verbose_name_plural = "Classgroup Schedules"

    # def __str__(self) -> str:
    #     return f"{self.classgroup} has schedule {self.student}"


#########################
#   REQUEST/INVITE
#########################


class ClassGroupStudentInviteOrRequest(models.Model):
    """"""

    _created_by = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name="created_inviterequest_classgroup",
    )

    _created_date = models.DateTimeField(auto_now_add=True)
    classgroup = models.ForeignKey(
        to=ClassGroup,
        on_delete=models.CASCADE,
        related_name="classgroup_inviterequest_student",
    )
    student = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name="student_inviterequest_classgroup",
    )
    invited = models.BooleanField(default=True)
    requested = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Classgroup Invites or Requests"

    def __str__(self) -> str:
        if self.invited:
            return f"ID={self.id} Invite: {self.student.username} to {self.classgroup}"

        elif self.requested:
            return f"ID={self.id} Request: {self.student.username} to {self.classgroup}"

    # TODO
    # @property
    # def create_notification(self):
    #     pass
