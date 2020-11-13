# Generated by Django 3.1.1 on 2020-10-18 18:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("response", "0019_meeting"),
    ]

    operations = [
        migrations.AddField(
            model_name="headlinepost",
            name="zoom_meeting",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="response.meeting",
            ),
        ),
    ]
