# Generated by Django 4.0.2 on 2022-02-20 16:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0001_initial'),
        ('classrooms', '0002_alter_classroom__created_by_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassroomHasSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classroom_schedule', to='classrooms.classroom')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedule_classroom', to='schedules.schedule')),
            ],
        ),
    ]