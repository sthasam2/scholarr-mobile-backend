# Generated by Django 4.0.2 on 2022-02-20 12:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('classroom_contents', '0001_initial'),
        ('classrooms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classroom',
            name='_created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_classroom', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='classroomhasstudent',
            name='classroom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classroom_student', to='classrooms.classroom'),
        ),
        migrations.AlterField(
            model_name='classroomhasstudent',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_classroom', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='classroomhasteacher',
            name='classroom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classroom_teacher', to='classrooms.classroom'),
        ),
        migrations.AlterField(
            model_name='classroomhasteacher',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_classroom', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ClassroomHasResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classroom_resource', to='classrooms.classroom')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resource_classroom', to='classroom_contents.resource')),
            ],
        ),
        migrations.CreateModel(
            name='ClassroomHasClasswork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classroom_classwork', to='classrooms.classroom')),
                ('classwork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classwork_classroom', to='classroom_contents.classwork')),
            ],
        ),
    ]
