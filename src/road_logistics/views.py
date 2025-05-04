import requests
import environ
from datetime import datetime
from requests.auth import HTTPBasicAuth


from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.base import ContentFile
from django.core.files import File
from django.contrib.gis.geos import GEOSGeometry

from road_logistics.models import Car, Ride, RidePoint
from utils.custom_django_functions import get_or_create_object

data_example = {
    "_id": 529201324,
    "formhub/uuid": "554c56d82231411b804a4bb06fcc4551",
    "start": "2024-01-29T10:51:13.633+02:00",
    "end": "2024-01-29T10:54:45.423+02:00",
    "username": "username not found",
    "deviceid": "ee-eu.kobotoolbox.org:yxsSEPffgpcaor4c",
    "group_start/car_model": "bmw",
    "group_start/car_number": "test",
    "group_start/km_start": "1",
    "group_start/photo_odometr": "logo-10_53_10.png",
    "group_start/aim": "bread",
    "group_start/point_start": "48.740051 37.582237 0 0",
    "group_start/__001": "До Покровська",
    "group_start/_point_1": "48.278295 37.176973 0 0",
    "group_finish/km_finish": "1000",
    "group_finish/photo_odometr_end": "logo-10_54_26.png",
    "group_finish/point_finish": "48.739358 37.583655 0 0",
    "group_finish/_": "yes",
    "group_finish/photo_check": "logo-10_54_38.png",
    "group_finish/fuel_count": "10",
    "__version__": "v6ZyNC7zVHqtJYvuiQ9raU",
    "meta/instanceID": "uuid:53958898-4dff-4ab0-9c9a-b21b5507f161",
    "_xform_id_string": "aNR7Yv3zUyeDT44DDpturD",
    "_uuid": "53958898-4dff-4ab0-9c9a-b21b5507f161",
    "_attachments": [
        {
            "download_url": "https://kc-eu.kobotoolbox.org/media/original?media_file=soovuh%2Fattachments%2F554c56d82231411b804a4bb06fcc4551%2F53958898-4dff-4ab0-9c9a-b21b5507f161%2Flogo-10_53_10.png",
            "download_large_url": "https://kc-eu.kobotoolbox.org/media/large?media_file=soovuh%2Fattachments%2F554c56d82231411b804a4bb06fcc4551%2F53958898-4dff-4ab0-9c9a-b21b5507f161%2Flogo-10_53_10.png",
            "download_medium_url": "https://kc-eu.kobotoolbox.org/media/medium?media_file=soovuh%2Fattachments%2F554c56d82231411b804a4bb06fcc4551%2F53958898-4dff-4ab0-9c9a-b21b5507f161%2Flogo-10_53_10.png",
            "download_small_url": "https://kc-eu.kobotoolbox.org/media/small?media_file=soovuh%2Fattachments%2F554c56d82231411b804a4bb06fcc4551%2F53958898-4dff-4ab0-9c9a-b21b5507f161%2Flogo-10_53_10.png",
            "mimetype": "image/png",
            "filename": "soovuh/attachments/554c56d82231411b804a4bb06fcc4551/53958898-4dff-4ab0-9c9a-b21b5507f161/logo-10_53_10.png",
            "instance": 529201324,
            "xform": 1572895,
            "id": 227995127,
        },
        {
            "download_url": "https://kc-eu.kobotoolbox.org/media/original?media_file=soovuh%2Fattachments%2F554c56d82231411b804a4bb06fcc4551%2F53958898-4dff-4ab0-9c9a-b21b5507f161%2Flogo-10_54_26.png",
            "download_large_url": "https://kc-eu.kobotoolbox.org/media/large?media_file=soovuh%2Fattachments%2F554c56d82231411b804a4bb06fcc4551%2F53958898-4dff-4ab0-9c9a-b21b5507f161%2Flogo-10_54_26.png",
            "download_medium_url": "https://kc-eu.kobotoolbox.org/media/medium?media_file=soovuh%2Fattachments%2F554c56d82231411b804a4bb06fcc4551%2F53958898-4dff-4ab0-9c9a-b21b5507f161%2Flogo-10_54_26.png",
            "download_small_url": "https://kc-eu.kobotoolbox.org/media/small?media_file=soovuh%2Fattachments%2F554c56d82231411b804a4bb06fcc4551%2F53958898-4dff-4ab0-9c9a-b21b5507f161%2Flogo-10_54_26.png",
            "mimetype": "image/png",
            "filename": "soovuh/attachments/554c56d82231411b804a4bb06fcc4551/53958898-4dff-4ab0-9c9a-b21b5507f161/logo-10_54_26.png",
            "instance": 529201324,
            "xform": 1572895,
            "id": 227995128,
        },
        {
            "download_url": "https://kc-eu.kobotoolbox.org/media/original?media_file=soovuh%2Fattachments%2F554c56d82231411b804a4bb06fcc4551%2F53958898-4dff-4ab0-9c9a-b21b5507f161%2Flogo-10_54_38.png",
            "download_large_url": "https://kc-eu.kobotoolbox.org/media/large?media_file=soovuh%2Fattachments%2F554c56d82231411b804a4bb06fcc4551%2F53958898-4dff-4ab0-9c9a-b21b5507f161%2Flogo-10_54_38.png",
            "download_medium_url": "https://kc-eu.kobotoolbox.org/media/medium?media_file=soovuh%2Fattachments%2F554c56d82231411b804a4bb06fcc4551%2F53958898-4dff-4ab0-9c9a-b21b5507f161%2Flogo-10_54_38.png",
            "download_small_url": "https://kc-eu.kobotoolbox.org/media/small?media_file=soovuh%2Fattachments%2F554c56d82231411b804a4bb06fcc4551%2F53958898-4dff-4ab0-9c9a-b21b5507f161%2Flogo-10_54_38.png",
            "mimetype": "image/png",
            "filename": "soovuh/attachments/554c56d82231411b804a4bb06fcc4551/53958898-4dff-4ab0-9c9a-b21b5507f161/logo-10_54_38.png",
            "instance": 529201324,
            "xform": 1572895,
            "id": 227995129,
        },
    ],
    "_status": "submitted_via_web",
    "_geolocation": [48.740051, 37.582237],
    "_submission_time": "2024-01-29T08:54:46",
    "_tags": [],
    "_notes": [],
    "_validation_status": {},
    "_submitted_by": None,
}

env = environ.Env()


def rides(request):
    query = request.GET.get("q")
    date_from_b = request.GET.get("date_from")
    date_to_b = request.GET.get("date_to")
    rides_list = Ride.objects.all().order_by("-id")
    if query:
        rides_list = rides_list.filter(
            Q(car__mark__icontains=query) | Q(car__number__icontains=query)
        )
    else:
        query = ''
    if date_from_b:
        date_from = datetime.strptime(date_from_b, "%Y-%m-%d")
        # Filter rides that occurred on or after date_from
        rides_list = rides_list.filter(date__gte=date_from)
    else:
        date_from_b = ''
    if date_to_b:
        date_to = datetime.strptime(date_to_b, "%Y-%m-%d")
        rides_list = rides_list.filter(date__lte=date_to)
    else:
        date_to_b = ''
    return render(request, "road_logistics/rides.html", {"rides": rides_list, "q": query, "date_from": date_from_b, "date_to": date_to_b})


def ride_detail(request, id):
    ride=Ride.objects.get(id=id)
    intermediate_points = RidePoint.objects.filter(ride=ride).order_by('number')
    points = [ride.start_point, ]
    for i in intermediate_points:
        points.append(i.point)
    points.append(ride.end_point)
    for point in points:
        print(point)
    return render(request, 'road_logistics/ride_detail.html', {"ride": ride, "points": points})


def search_kobo_image(name, attachments):
    for a in attachments:
        if a["download_url"].endswith(name):
            link = a["download_url"]
            response = requests.get(link, auth=HTTPBasicAuth(env("KOBO_USERNAME"), env("KOBO_PASSWORD")))
            image_content = ContentFile(response.content)
            return image_content, name
    return None, None
    

class FetchKoboAPI(APIView):
    def post(self, request, *args, **kwargs):
        data = data_example
        car_mark = data["group_start/car_model"].lower()
        car_number = data["group_start/car_number"].lower()
        car = get_or_create_object(Car, mark=car_mark, number=car_number)
        
        attachments = data["_attachments"]

        start_point_coords = [float(i) for i in data["group_start/point_start"].split(' ')]
        start_point = GEOSGeometry(f"POINT({start_point_coords[1]} {start_point_coords[0]})")
        start_odometer_kilometres = float(data["group_start/km_start"])
        start_odometer_content, start_odometer_name = search_kobo_image(data["group_start/photo_odometr"], attachments)
    
        note_start = data["group_start/__001"] if "group_start/__001" in data.keys() else ''
        note_end = data["group_group_finish/note_end"] if "group_group_finish/note_end" in data.keys() else ''

        end_point_coords = [float(i) for i in data["group_finish/point_finish"].split(' ')]
        end_point = GEOSGeometry(f"POINT({end_point_coords[1]} {end_point_coords[0]})")

        end_odometer_kilometres = float(data["group_finish/km_finish"])
        end_odometer_content, end_odometer_name = search_kobo_image(data["group_finish/photo_odometr_end"], attachments)

        is_refueling = True if data['group_finish/_']=='yes' else False
        if is_refueling:
            refueling_check_content, refueling_check_name = search_kobo_image(data["group_finish/photo_check"], attachments)
            fuel_litre = data["group_finish/fuel_count"]
        else:
            refueling_check_content, refueling_check_name = None, None
            fuel_litre = None
        mission = data["group_start/aim"]
        ride = Ride.objects.create(
            car=car,
            start_point=start_point,
            start_odometer_kilometres=start_odometer_kilometres,
            note_start=note_start,
            end_point=end_point,
            end_odometer_kilometres=end_odometer_kilometres,
            is_refueling=is_refueling,
            fuel_litre=fuel_litre,
            mission=mission,
            note_end=note_end
        )
        ride.start_odometer_photo.save(start_odometer_name, File(start_odometer_content))
        ride.end_odometer_photo.save(end_odometer_name, File(end_odometer_content))
        if is_refueling:
            ride.refueling_check.save(refueling_check_name, File(refueling_check_content))
        for x in range(1, 6):
            if f"group_start/_point_{x}" in data.keys():
                point_coords = [float(i) for i in data[f"group_start/_point_{x}"].split(' ')]
                RidePoint.objects.create(number=x, ride=ride,
                    point=GEOSGeometry(f"POINT({point_coords[1]} {point_coords[0]})"))    
            else:
                break
        return Response({"message": "Data received successfully"})
    

