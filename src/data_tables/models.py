import os
import json
from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


from accounts.models import CustomUser
from reports.models import Project, Category
from activity_map.models import Place


geojson_oblasts_names = {
    "Donetska": "Donetsk Oblast",
    "Zaporizka": "Zaporizhia Oblast",
    "Kharkivska": "Kharkiv Oblast",
    "Khersonska": "Kherson Oblast",
    "Luhanska": "Luhansk Oblast",
    "Dnipropetrovska": "Dnipropetrovsk Oblast",
    "Mykolaivska": "Mykolaiv Oblast",
}


def get_file_path(instance, filename):
    return os.path.join(
        "downloaded_files", instance.project.name, instance.category.name, filename
    )


def get_photo_path(instance, filename):
    return os.path.join(instance.project.name, instance.category.name, filename)


class TableDownload(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    download_date = models.DateTimeField(default=timezone.now)
    xlsx_file = models.FileField(upload_to="generated_reports", null=True, blank=True)
    pdf_file = models.FileField(upload_to="generated_reports", null=True, blank=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, related_name="project_name"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="category_name"
    )


class RegionStatistic(models.Model):
    name = models.CharField(blank=True, null=True, max_length=100)
    project = models.ForeignKey(
        to=Project, on_delete=models.CASCADE, blank=True, null=True
    )
    oblast = models.CharField(max_length=100)
    benef = models.IntegerField()
    activities = models.ManyToManyField(Category)

    def __str__(self) -> str:
        return f"Oblast: {self.name}; Project: {self.project.name}"


class DataTable(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, related_name="data_entries"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="data_entries"
    )
    photo = models.ImageField(upload_to=get_photo_path, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    place = models.ForeignKey(
        to=Place, on_delete=models.SET_NULL, null=True, blank=True
    )
    date = models.DateField(null=True, blank=True)
    demography = models.JSONField(blank=True, null=True)
    received_items = models.JSONField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.demography and self.place:
            demography = json.loads(self.demography)
            name = self.place.oblast
            benef = demography["benef"]
            try:
                region = RegionStatistic.objects.get(name=name, project=self.project)
                region.benef += benef
                if not region.activities.filter(id=self.category.id).exists():
                    region.activities.add(self.category)

                region.save()
            except ObjectDoesNotExist:
                oblast = geojson_oblasts_names.get(name)

                region = RegionStatistic.objects.create(
                    name=name, oblast=oblast, benef=benef, project=self.project
                )
                region.activities.add(self.category)
                region.save()
        super().save(*args, **kwargs)
