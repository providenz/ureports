import os
import django
import json
import pandas as pd
import numpy as np


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "volunteer_reports.settings")
django.setup()

from activity_map.models import Place, Marker
from reports.models import Project, Category
from django.contrib.gis.geos import GEOSGeometry


def main():
    file_path = "Kharkiv region.xlsx"
    df = pd.read_excel(file_path)

    for index, row in df.iterrows():
        # Access the values in each row using column names
        settlement = row["Sttlement"]
        print(settlement)
        lat = row["lat"]
        lon = row["lon"]
        if np.isnan(settlement):
            continue
        try:
            place = Place.objects.get(oblast="Kharkivska", settlement=settlement)
        except Place.DoesNotExist:
            place = Place.objects.create(
                oblast="Kharkivska",
                rayon="Kharkivsky",
                gromada="Kharkivska",
                settlement=settlement,
            )

        location_point = GEOSGeometry(f"POINT({lon} {lat})")
        category = Category.objects.get(name="Small Reabilitaion")
        project = Project.objects.get(name="US_UKR22_SV_007")
        marker = Marker.objects.create(
            project=project, category=category, place=place, location=location_point
        )
        marker.save()


if __name__ == "__main__":
    main()
