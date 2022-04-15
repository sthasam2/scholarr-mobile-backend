from django.db import models


class Classroom(models.Model):
    """Modelling a classroom with a teacher and their students"""

    _created_by = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name="created_classroom",
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
#   REQUEST/INVITE
#########################


class ClassroomInviteOrRequest(models.Model):
    """Model for inviting or requesting classroom"""

    class TargetChoices(models.TextChoices):
        """Invite/Request Type"""

        CLASSGROUP = "C", "Class Group"
        STUDENT = "S", "Student"
        TEACHER = "T", "Teacher"

    _created_by = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name="created_classroom_inviterequest",
    )
    _created_date = models.DateTimeField(auto_now_add=True)
    _modified_date = models.DateTimeField(auto_now=True)

    target_type = models.CharField(max_length=1, choices=TargetChoices.choices)

    invited = models.BooleanField(default=True)
    requested = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)

    classroom = models.ForeignKey(
        to=Classroom,
        on_delete=models.CASCADE,
        related_name="classroom_inviterequest",
        null=True,
        blank=True,
    )
    classgroup = models.ForeignKey(
        to="class_groups.ClassGroup",
        on_delete=models.CASCADE,
        related_name="classgroup_inviterequest_classroom",
        null=True,
        blank=True,
    )
    student = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name="student_inviterequest_classroom",
        null=True,
        blank=True,
    )
    teacher = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name="teacher_inviterequest_classroom",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = "Classrooms Invites or Requests"

    def __str__(self):
        return f"ID={self.id}, target={self.target_type}"


#########################
#   RELATIONSHIPS
#########################

# Custom User Relationships


class ClassroomHasTeacher(models.Model):
    """Relation between Classroom and Teacher"""

    classroom = models.ForeignKey(
        to=Classroom,
        on_delete=models.CASCADE,
        related_name="classroom_teacher",
    )
    teacher = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name="teacher_classroom",
    )

    class Meta:
        verbose_name_plural = "Classroom Teachers"


class ClassroomHasStudent(models.Model):
    """Relation between Classroom and Student"""

    classroom = models.ForeignKey(
        to=Classroom,
        on_delete=models.CASCADE,
        related_name="classroom_student",
    )
    student = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name="student_classroom",
    )

    class Meta:
        verbose_name_plural = "Classroom Students"


# Classwork/ Content Relationships


class ClassroomHasClasswork(models.Model):
    """Relation between Classroom and Student"""

    classroom = models.ForeignKey(
        to=Classroom,
        on_delete=models.CASCADE,
        related_name="classroom_classwork",
    )
    classwork = models.ForeignKey(
        to="classroom_contents.Classwork",
        on_delete=models.CASCADE,
        related_name="classwork_classroom",
    )

    class Meta:
        verbose_name_plural = "Classroom Classworks"


class ClassroomHasResource(models.Model):
    """Relation between Classroom and Student"""

    classroom = models.ForeignKey(
        to=Classroom,
        on_delete=models.CASCADE,
        related_name="classroom_resource",
    )
    resource = models.ForeignKey(
        to="classroom_contents.Resource",
        on_delete=models.CASCADE,
        related_name="resource_classroom",
    )

    class Meta:
        verbose_name_plural = "Classroom Resources"


# Schedule Relationships


class ClassroomHasSchedule(models.Model):
    """Relation between Classroom and Student"""

    classroom = models.ForeignKey(
        to=Classroom,
        on_delete=models.CASCADE,
        related_name="classroom_schedule",
    )
    schedule = models.ForeignKey(
        to="schedules.Schedule",
        on_delete=models.CASCADE,
        related_name="schedule_classroom",
    )

    class Meta:
        verbose_name_plural = "Classroom Schedules"
