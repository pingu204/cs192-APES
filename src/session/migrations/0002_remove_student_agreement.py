# Generated by Django 5.1.5 on 2025-02-07 11:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("session", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="student",
            name="agreement",
        ),
    ]
