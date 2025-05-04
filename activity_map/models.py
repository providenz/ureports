from django.contrib.gis.db import models

from reports.models import Category, Project


class Place(models.Model):
    oblast = models.CharField(max_length=255)
    rayon = models.CharField(max_length=255)
    gromada = models.CharField(max_length=255)
    settlement = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.settlement} - {self.gromada} - {self.rayon} - {self.oblast}"


class Marker(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE)
    place = models.ForeignKey(to=Place, on_delete=models.CASCADE)
    location = models.PointField()

    def __str__(self):
        return f" {self.place} - {self.project} - {self.category.name}"
