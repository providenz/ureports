# Generated by Django 4.2.6 on 2024-01-18 13:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "slug",
                    models.SlugField(
                        blank=True, max_length=250, null=True, unique=True
                    ),
                ),
                (
                    "icon",
                    models.CharField(
                        choices=[
                            ("fa-bread-slice", "fa-bread-slice"),
                            ("fa-tint", "fa-tint"),
                            ("fa-utensils", "fa-utensils"),
                            ("bag-shopping", "bag-shopping"),
                            ("truck-fast", "truck-fast"),
                            ("fa-hammer", "fa-hammer"),
                            ("hands-bubbles", "hands-bubbles"),
                        ],
                        default="fa-bread-slice",
                        max_length=50,
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        choices=[
                            ("red", "red"),
                            ("blue", "blue"),
                            ("green", "green"),
                            ("purple", "purple"),
                            ("orange", "orange"),
                            ("darkred", "darkred"),
                            ("gray", "gray"),
                        ],
                        default="orange",
                        max_length=50,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Dashboard",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("total_benef", models.IntegerField()),
                ("avg_people_in_family", models.FloatField()),
                ("female_percent", models.FloatField()),
                ("male_percent", models.FloatField()),
                ("children_percent", models.FloatField()),
                ("over_60_percent", models.FloatField()),
                ("pwd_percent", models.FloatField()),
                ("total_qty", models.IntegerField()),
                ("male_60plus", models.FloatField()),
                ("male_5_17", models.FloatField()),
                ("male_0_4", models.FloatField()),
                ("male_18_59", models.FloatField()),
                ("female_60plus", models.FloatField()),
                ("female_5_17", models.FloatField()),
                ("female_0_4", models.FloatField()),
                ("female_18_59", models.FloatField()),
                ("region_stats", models.JSONField(blank=True, null=True)),
                ("received_items_stats", models.JSONField(blank=True, null=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="reports.category",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UpdateDashboard",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField(default=django.utils.timezone.now)),
                ("total_benef", models.IntegerField()),
                ("females", models.IntegerField()),
                ("males", models.IntegerField()),
                ("children", models.IntegerField()),
                ("over_60", models.IntegerField()),
                ("pwds", models.IntegerField()),
                ("total_qty", models.IntegerField()),
                ("male_60plus", models.IntegerField()),
                ("male_18_59", models.IntegerField()),
                ("male_5_17", models.IntegerField()),
                ("male_0_4", models.IntegerField()),
                ("female_60plus", models.IntegerField()),
                ("female_18_59", models.IntegerField()),
                ("female_5_17", models.IntegerField()),
                ("female_0_4", models.IntegerField()),
                ("region_stats", models.JSONField(blank=True, null=True)),
                ("received_items_stats", models.JSONField(blank=True, null=True)),
                (
                    "dashboard",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="reports.dashboard",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("goal", models.TextField()),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "slug",
                    models.SlugField(
                        blank=True, max_length=250, null=True, unique=True
                    ),
                ),
                (
                    "categories",
                    models.ManyToManyField(
                        blank=True, related_name="projects", to="reports.category"
                    ),
                ),
                (
                    "donors",
                    models.ManyToManyField(
                        related_name="donated_projects", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="dashboard",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="reports.project"
            ),
        ),
    ]
