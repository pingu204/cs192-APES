# Generated by Django 5.1.5 on 2025-04-08 20:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0002_savedcourse_alter_desiredcourse_course_code_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="savedschedule",
            name="preferences",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
