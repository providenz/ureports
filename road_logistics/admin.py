from django.contrib import admin

from road_logistics.models import Car, Ride, RidePoint


admin.site.register(Car)
admin.site.register(Ride)
admin.site.register(RidePoint)