from django.db import models
from accounts.models import CustomUser
import os
from django.utils import timezone

from django.template.defaultfilters import slugify

ACTIVITY_ICONS = {
    "Bread Distribution": "fa-bread-slice",
    "Water distribution": "fa-tint",
    "Food Distribution": "fa-utensils",
    "Non-Food Items (NFI)": "bag-shopping",
    "Evacuation": "truck-fast",
    "Restoration of a damaged home": "fa-hammer",
    "Hygiene": "hands-bubbles",
}

ACTIVITY_COLORS = {
    "Bread Distribution": "red",
    "Water distribution": "blue",
    "Food Distribution": "green",
    "Non-Food Items (NFI)": "purple",
    "Evacuation": "orange",
    "Restoration of a damaged home": "darkred",
    "Hygiene": "gray",
}


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, max_length=250, unique=True)
    icon = models.CharField(
        max_length=50,
        choices=[(icon, icon) for icon in ACTIVITY_ICONS.values()],
        default="fa-bread-slice",
    )
    color = models.CharField(
        max_length=50,
        choices=[(color, color) for color in ACTIVITY_COLORS.values()],
        default="orange",
    )

    def __str__(self):
        return self.name

    # Set slug on save
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if "_" in self.slug:
            self.slug = self.slug.replace("_", "-")
        return super().save(*args, **kwargs)


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    goal = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    donors = models.ManyToManyField(CustomUser, related_name="donated_projects")
    categories = models.ManyToManyField(Category, related_name="projects", blank=True)
    slug = models.SlugField(blank=True, null=True, max_length=250, unique=True)

    def __str__(self):
        return self.name

    # Set slug on save
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if "_" in self.slug:
            self.slug = self.slug.replace("_", "-")
        return super().save(*args, **kwargs)


class Dashboard(models.Model):
    # foreign keys
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # general info
    total_benef = models.IntegerField()
    avg_people_in_family = models.FloatField()
    female_percent = models.FloatField()
    male_percent = models.FloatField()
    children_percent = models.FloatField()
    over_60_percent = models.FloatField()
    pwd_percent = models.FloatField()

    # distribution qty info
    total_qty = models.IntegerField()

    # demography info
    male_60plus = models.FloatField()
    male_18_59 = models.FloatField()
    male_5_17 = models.FloatField()
    male_0_4 = models.FloatField()
    male_18_59 = models.FloatField()
    female_60plus = models.FloatField()
    female_18_59 = models.FloatField()
    female_5_17 = models.FloatField()
    female_0_4 = models.FloatField()
    female_18_59 = models.FloatField()

    # statistic by place
    region_stats = models.JSONField(blank=True, null=True)
    received_items_stats = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.project}, {self.category}"


class UpdateDashboard(models.Model):
    date = models.DateField(default=timezone.now)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE)

    # general info
    total_benef = models.IntegerField()
    females = models.IntegerField()
    males = models.IntegerField()
    children = models.IntegerField()
    over_60 = models.IntegerField()
    pwds = models.IntegerField()

    # distribution qty info
    total_qty = models.IntegerField()

    # demography info
    male_60plus = models.IntegerField()
    male_18_59 = models.IntegerField()
    male_5_17 = models.IntegerField()
    male_0_4 = models.IntegerField()
    female_60plus = models.IntegerField()
    female_18_59 = models.IntegerField()
    female_5_17 = models.IntegerField()
    female_0_4 = models.IntegerField()

    # demography info
    region_stats = models.JSONField(blank=True, null=True)
    received_items_stats = models.JSONField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.date}  {self.dashboard}"
