# Generated by Django 4.0.2 on 2022-05-08 14:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classroom_contents', '0005_alter_attachment_model_dump_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlagiarismInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage_plagiarized', models.FloatField()),
                ('submission_agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submission_agent_plagiarism', to='classroom_contents.submission')),
                ('submission_target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submission_target_plagiarism', to='classroom_contents.submission')),
            ],
            options={
                'verbose_name_plural': 'Plagiarism Information',
            },
        ),
    ]
