# Generated by Django 4.2.6 on 2024-01-29 12:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("road_logistics", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ride",
            name="date",
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
