from rest_framework import serializers

from apps.classroom_contents.models import Attachment, Classwork, Resource, Submission
from apps.users.api.serializers import PublicUserSerializer

#########################
#   CONTENT
#########################

## CLASSWORK


class CreateClassworkSerializer(serializers.ModelSerializer):
    """"""

    title = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500, required=False)
    content_type = serializers.CharField(max_length=3, required=False)
    deadline = serializers.DateTimeField(required=False)
    weightage = serializers.IntegerField(required=False)

    class Meta:
        model = Classwork
        fields = ["title", "description", "content_type", "deadline", "weightage"]


class UpdateClassworkSerializer(serializers.ModelSerializer):
    """"""

    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(max_length=500, required=False)
    content_type = serializers.CharField(max_length=3, required=False)
    weightage = serializers.IntegerField(required=False)

    class Meta:
        model = Classwork
        fields = ["title", "description", "content_type", "weightage"]


class ReadClassworkSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = Classwork
        fields = "__all__"


## RESOURCE


class CreateResourceSerializer(serializers.ModelSerializer):
    """"""

    title = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500, required=False)
    content_type = serializers.CharField(max_length=3, required=False)

    class Meta:
        model = Resource
        fields = ["title", "description", "content_type"]


class UpdateResourceSerializer(serializers.ModelSerializer):
    """"""

    title = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500, required=False)
    content_type = serializers.CharField(max_length=3, required=False)

    class Meta:
        model = Resource
        fields = ["title", "description", "content_type"]


class ReadResourceSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = Resource
        fields = "__all__"


## SUBMISSION


class CreateSubmissionSerializer(serializers.ModelSerializer):
    """"""

    answer = serializers.CharField(max_length=5000, required=False)

    class Meta:
        model = Submission
        fields = ["answer"]


class UpdateSubmissionSerializer(serializers.ModelSerializer):
    """"""

    answer = serializers.CharField(max_length=5000, required=False)

    remarks = serializers.CharField(max_length=5000, required=False)
    grade = serializers.IntegerField(required=False)

    class Meta:
        model = Submission
        fields = ["answer", "remarks", "grade"]


class ReadSubmissionSerializer(serializers.ModelSerializer):
    """"""

    _created_by = PublicUserSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = "__all__"


#########################
#   ATTACHMENT
#########################


class AttachmentSerializer(serializers.ModelSerializer):
    """"""

    attachment = serializers.FileField()

    class Meta:
        model = Attachment
        fields = ["attachment", "mime_type"]


class ReadAttachmentSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = Attachment
        fields = "__all__"
