from rest_framework import serializers

from apps.plagiarism_detector.models import PlagiarismInfo
from apps.classroom_contents.api.serializers import ReadSubmissionSerializer


class PlagiarismSerializer(serializers.ModelSerializer):
    """"""

    submission_agent = ReadSubmissionSerializer(read_only=True)
    submission_target = ReadSubmissionSerializer(read_only=True)

    class Meta:
        model = PlagiarismInfo
        fields = "__all__"
