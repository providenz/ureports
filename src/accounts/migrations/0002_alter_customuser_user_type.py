# Generated by Django 4.2.6 on 2024-01-25 08:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="user_type",
            field=models.CharField(
                choices=[("AD", "Admin"), ("DO", "Donor"), ("MA", "Manager")],
                default="DO",
                max_length=2,
            ),
        ),
    ]
