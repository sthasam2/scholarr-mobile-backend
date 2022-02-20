from django.db import models


class Schedule(models.Model):
    """ """

    class DayChoices(models.TextChoices):
        """Day options"""

        SUN = 1, "SUNDAY"
        MON = 2, "MONDAY"
        TUE = 3, "TUESDAY"
        WED = 4, "WEDNESDAY"
        THU = 5, "THURSDAY"
        FRI = 6, "FRIDAY"
        SAT = 7, "SATURDAY"

    day = models.PositiveIntegerField(
        choices=DayChoices.choices,
        help_text="Pick from 1 to 7, 1 being Sunday and 7 being Saturday",
    )
    time_start = models.TimeField()
    time_end = models.TimeField()
    room = models.CharField(max_length=20, null=True, blank=True)
    link = models.CharField(max_length=1000, null=True, blank=True)
    note = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.day} @{self.time_start} - {self.time_end}"
