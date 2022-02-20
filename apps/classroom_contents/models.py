from django.db import models
from apps.users.models import CustomUser

# from apps.classrooms.models import Classroom

#########################
#   ABSTRACT
#########################


class AbstractContent(models.Model):
    """"""

    _created_by = models.ForeignKey(
        to=CustomUser, on_delete=models.CASCADE, related_name="created_%(class)s"
    )

    _created_date = models.DateTimeField(auto_now_add=True)
    _modified_date = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=5000)

    modified = models.BooleanField(default=False)
    attachments = models.BooleanField(default=False)

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

        ASSIGNMENT = "A", "ASSIGNMENT"
        QUESTION = "Q", "QUESTION"
        TEST = "T", "TEST"
        POLL = "P", "POLL"
        DEFAULT = "D", "DEFAULT"

    # _created_by = models.ForeignKey(
    #     to=CustomUser, on_delete=models.CASCADE, related_name="created_classwork"
    # )

    type = models.CharField(max_length=1, choices=ClassworkChoices.choices)

    def __str__(self) -> str:
        return f"{self.type} -> {self.title}"


class Resource(AbstractContent):
    """"""

    class ResourceChoices(models.TextChoices):
        """Resource Types"""

        NOTES = "N", "NOTES"
        BOOKS = "B", "BOOKS"
        LECTURE_PLAN = "LP", "LECTURE_PLAN"
        MEDIA = "M", "MEDIA"
        LINKS = "L", "LINKS"
        DEFAULT = "D", "DEFAULT"

    type = models.CharField(max_length=2, choices=ResourceChoices.choices)

    def __str__(self) -> str:
        return f"{self.type} -> {self.title}"


class Attachment(models.Model):
    """"""

    _created_at = models.DateTimeField(auto_now_add=True)

    file = models.FileField(upload_to="%(app_name)s_files/")
    type = models.CharField(max_length=100, null=True, blank=True)

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
