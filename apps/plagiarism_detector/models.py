from tabnanny import verbose
from django.db import models

from apps.classroom_contents.models import Submission

# Create your models here.
class PlagiarismInfo(models.Model):
    """ """

    submission_agent = models.ForeignKey(
        to=Submission,
        related_name="submission_agent_plagiarism",
        on_delete=models.CASCADE,
    )
    submission_target = models.ForeignKey(
        to=Submission,
        related_name="submission_target_plagiarism",
        on_delete=models.CASCADE,
    )
    percentage_plagiarized = models.FloatField()

    class Meta:
        verbose_name_plural = "Plagiarism Information"
