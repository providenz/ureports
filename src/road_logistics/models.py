from django.contrib.gis.db import models
from django.utils import timezone



class Car(models.Model):
    mark = models.CharField(max_length=255)
    number = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.mark} - {self.number}"


class Ride(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)


    start_point = models.PointField()
    start_odometer_kilometres = models.PositiveBigIntegerField()
    start_odometer_photo = models.ImageField(upload_to="road_logistics/odometer/start/", blank=True, null=True)
    note_start = models.CharField(max_length=300, blank=True, null=True)

    end_point = models.PointField()
    end_odometer_kilometres = models.PositiveBigIntegerField()
    end_odometer_photo = models.ImageField(upload_to="road_logistics/odometer/end/", blank=True, null=True)
    note_end = models.CharField(max_length=300, blank=True, null=True)

    is_refueling = models.BooleanField()
    refueling_check = models.ImageField("road_logistics/checks/", blank=True, null=True)
    fuel_litre = models.IntegerField(blank=True, null=True)

    mission = models.CharField(max_length=300)

    def __str__(self) -> str:
        return f'{self.car} - {self.date}'


class RidePoint(models.Model):
    number = models.IntegerField()
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    point = models.PointField()
    
    def __str__(self) -> str:
        return f'{self.number} - {self.ride}'