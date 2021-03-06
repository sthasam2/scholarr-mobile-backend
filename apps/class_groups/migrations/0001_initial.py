# Generated by Django 4.0.2 on 2022-04-09 13:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ClassGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("_created_date", models.DateTimeField(auto_now_add=True)),
                ("_modified_date", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("classgroup_code", models.CharField(max_length=32)),
                ("faculty", models.CharField(max_length=200)),
                ("batch", models.CharField(max_length=200)),
                ("organisation", models.CharField(max_length=200)),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name_plural": "ClassGroups",
            },
        ),
        migrations.CreateModel(
            name="ClassGroupStudentInviteOrRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("invited", models.BooleanField(default=True)),
                ("requested", models.BooleanField(default=False)),
                ("accepted", models.BooleanField(default=False)),
                ("rejected", models.BooleanField(default=False)),
                (
                    "classgroup",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="classgroup_inviterequest_student",
                        to="class_groups.classgroup",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_inviterequest_classgroup",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_inviterequest_classgroup",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Classgroup Invites or Requests",
            },
        ),
        migrations.CreateModel(
            name="ClassGroupHasStudent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "classgroup",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="classgroup_student",
                        to="class_groups.classgroup",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_classgroup",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Classgroup Students",
            },
        ),
        migrations.CreateModel(
            name="ClassGroupHasRoutineSchedules",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "classgroup",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="classgroup_schedule",
                        to="class_groups.classgroup",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Classgroup Schedules",
            },
        ),
        migrations.CreateModel(
            name="ClassGroupHasClassroom",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "classgroup",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="classgroup_classroom",
                        to="class_groups.classgroup",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Classgroup Classrooms",
            },
        ),
    ]
