from rest_framework import serializers

from apps.classrooms.api.serializers import ClassroomOnlySerializer
from apps.schedules.models import Schedule


class CreateScheduleSerializer(serializers.ModelSerializer):
    """ """

    day = serializers.IntegerField()
    time_start = serializers.TimeField()
    time_end = serializers.TimeField()
    room = serializers.CharField(max_length=20, required=False)
    link = serializers.CharField(max_length=1000, required=False)
    note = serializers.CharField(max_length=500, required=False)

    class Meta:
        model = Schedule
        fields = ["day", "time_start", "time_end", "room", "link", "note"]


class UpdateScheduleSerializer(serializers.ModelSerializer):
    """ """

    day = serializers.IntegerField(required=False)
    time_start = serializers.TimeField(required=False)
    time_end = serializers.TimeField(required=False)
    room = serializers.CharField(max_length=20, required=False)
    link = serializers.CharField(max_length=1000, required=False)
    note = serializers.CharField(max_length=500, required=False)

    class Meta:
        model = Schedule
        fields = ["day", "time_start", "time_end", "room", "link", "note"]


class ReadScheduleSerializer(serializers.ModelSerializer):
    """ """

    class Meta:
        model = Schedule
        fields = "__all__"


class ScheduleClassroomSerializer(ClassroomOnlySerializer):
    pass
