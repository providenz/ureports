import os
import django
import json

import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "volunteer_reports.settings")
django.setup()

from reports.models import Project, Category
from data_tables.models import DataTable
from activity_map.models import Place, Marker
from django.contrib.gis.geos import GEOSGeometry
import random
from utils.custom_django_functions import get_or_create_object


def upload_new_data(total, current, xlsx_path):
    project = Project.objects.get(name="US_UKR22_SV_007")
    category = Category.objects.get(name="Non-Food Items (NFI)")
    df = pd.read_excel(xlsx_path)
    df["date_day"] = pd.to_datetime(df["date_day"], errors="coerce")

    for index, row in df.iterrows():
        if current == total:
            break
        place = get_or_create_object(
            Place,
            settlement=row["location_label"],
            gromada=row["gromada"],
            rayon=row["rayon"],
            oblast=row["oblast"],
        )
        marker = get_or_create_object(
            Marker,
            place=place,
            category=category,
            project=project,
            location=GEOSGeometry(f"POINT({row['longitude']} {row['latitude']})"),
        )
        current += int(row["benef"])
        if current > total:
            benef = int(row["benef"]) - (current - total)
            current = total
        else:
            benef = int(row["benef"])
        demography = json.dumps(
            {
                "benef": benef,
                "female_0_4": row["female_0_4"],
                "female_5_17": row["female_5_17"],
                "female_18_59": row["female_18_59"],
                "female_60plus": row["female_60plus"],
                "male_0_4": row["male_0_4"],
                "male_5_17": row["male_5_17"],
                "male_18_59": row["male_18_59"],
                "male_60plus": row["male_60plus"],
                "male_PWD": row["male_PWD"],
                "female_PWD": row["female_PWD"],
                "female_benef": row["female_benef"],
                "male_benef": row["male_benef"],
            }
        )
        received_items = json.dumps({row["activity"]: row["unit"]})

        entry = DataTable.objects.create(
            project=project,
            category=category,
            gender=random.choice(["male", "female"]),
            age=random.randint(18, 80),
            place=place,
            date=row["date_day"],
            demography=demography,
            received_items=received_items,
        )
        entry.save()


def main():
    current = 9526
    total = 53509
    xlsx_path = "Shelter.xlsx"

    upload_new_data(total, current, xlsx_path)


if __name__ == "__main__":
    main()
