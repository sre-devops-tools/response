# Generated by Django 3.1.1 on 2020-10-18 17:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("response", "0018_remove_incident_zoom_meeting"),
    ]

    operations = [
        migrations.CreateModel(
            name="Meeting",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("weblink", models.CharField(max_length=255)),
                ("challenge", models.CharField(max_length=100)),
                (
                    "incident",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="response.incident",
                    ),
                ),
            ],
        ),
    ]
