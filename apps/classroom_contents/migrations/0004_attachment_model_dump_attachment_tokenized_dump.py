# Generated by Django 4.0.2 on 2022-05-08 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom_contents', '0003_classwork_deadline'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='model_dump',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='attachment',
            name='tokenized_dump',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]