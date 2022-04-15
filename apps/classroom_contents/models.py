from django.db import models

# from apps.classrooms.models import Classroom

#########################
#   ABSTRACT
#########################


class AbstractContent(models.Model):
    """"""

    _created_by = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name="created_%(class)s",
    )

    _created_date = models.DateTimeField(auto_now_add=True)
    _modified_date = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=5000)

    modified = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title


#########################
#   CONTENTS
#########################


class Classwork(AbstractContent):
    """"""

    class ClassworkChoices(models.TextChoices):
        """Classwork Types"""

        ASSIGNMENT = "C_A", "ASSIGNMENT"
        QUESTION = "C_Q", "QUESTION"
        TEST = "C_T", "TEST"
        POLL = "C_P", "POLL"
        DEFAULT = "C_D", "DEFAULT"

    # _created_by = models.ForeignKey(
    #     to="users.CustomUser", on_delete=models.CASCADE, related_name="created_classwork"
    # )

    content_type = models.CharField(
        max_length=3, default="C_D", choices=ClassworkChoices.choices
    )
    weightage = models.PositiveBigIntegerField(default=100)
    attachments = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.content_type} -> {self.title}"


class Resource(AbstractContent):
    """"""

    class ResourceChoices(models.TextChoices):
        """Resource Types"""

        NOTES = "R_N", "NOTES"
        BOOKS = "R_B", "BOOKS"
        LECTURE_PLAN = "R_LP", "LECTURE_PLAN"
        MEDIA = "R_M", "MEDIA"
        LINKS = "R_L", "LINKS"
        DEFAULT = "R_D", "DEFAULT"

    content_type = models.CharField(max_length=4, choices=ResourceChoices.choices)
    attachments = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.content_type} -> {self.title}"


class Submission(models.Model):
    """"""

    _created_by = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name="created_%(class)s",
    )

    _created_date = models.DateTimeField(auto_now_add=True)
    _modified_date = models.DateTimeField(auto_now=True)

    answer = models.CharField(max_length=5000)

    grade = models.PositiveIntegerField(default=0)
    remarks = models.CharField(max_length=5000)

    modified = models.BooleanField(default=False)
    graded = models.BooleanField(default=False)
    attachments = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.type} -> {self.title}"


class Attachment(models.Model):
    """"""

    _created_at = models.DateTimeField(auto_now_add=True)

    attachment = models.FileField(upload_to="%(app_name)s_files/")
    mime_type = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self) -> str:
        return self.file.path


#########################
#   RELATIONSHIPS
#########################


class ClassworkHasAttachment(models.Model):
    """"""

    attachment = models.ForeignKey(
        to=Attachment, on_delete=models.CASCADE, related_name="attachment_classwork"
    )
    classwork = models.ForeignKey(
        to=Classwork, on_delete=models.CASCADE, related_name="classwork_attachment"
    )


class ResourceHasAttachment(models.Model):
    """"""

    attachment = models.ForeignKey(
        to=Attachment, on_delete=models.CASCADE, related_name="attachment_resource"
    )
    resource = models.ForeignKey(
        to=Resource, on_delete=models.CASCADE, related_name="resource_attachment"
    )


class ClassworkHasSubmission(models.Model):
    """ """

    submission = models.ForeignKey(
        to=Submission, on_delete=models.CASCADE, related_name="submission_classwork"
    )
    classwork = models.ForeignKey(
        to=Classwork, on_delete=models.CASCADE, related_name="classwork_submission"
    )


class SubmissionHasAttachment(models.Model):
    """"""

    attachment = models.ForeignKey(
        to=Attachment, on_delete=models.CASCADE, related_name="attachment_submission"
    )
    submission = models.ForeignKey(
        to=Submission, on_delete=models.CASCADE, related_name="submission_attachment"
    )
