import os
import django
import json

import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "volunteer_reports.settings")
django.setup()

from reports.models import Project, Category
from data_tables.models import DataTable
from activity_map.models import Place, Marker


def load_data(entries, excel):
    for entry in entries:
        place = entry.place
        point = Marker.objects.filter(place=place).first().location
        latitude, longitude = point.y, point.x
        demography = json.loads(entry.demography)
        received_items = json.loads(entry.received_items)
        row = {
            "date": entry.date,
            "project": entry.project.name,
            "category": entry.category.name,
            "photo": entry.photo,
            "gender": entry.gender,
            "age": entry.age,
            "oblast": place.oblast,
            "rayon": place.rayon,
            "gromada": place.gromada,
            "settlement": place.settlement,
            "latitude": latitude,
            "longitude": longitude,
            "benef": demography["benef"],
            "female_0_4": demography["female_0_4"],
            "female_5_17": demography["female_5_17"],
            "female_18_59": demography["female_18_59"],
            "female_60plus": demography["female_60plus"],
            "male_0_4": demography["male_0_4"],
            "male_5_17": demography["male_5_17"],
            "male_18_59": demography["male_18_59"],
            "male_60plus": demography["male_60plus"],
            "female_pwd": demography["female_PWD"],
            "male_pwd": demography["male_PWD"],
            "female_benef": demography["female_benef"],
            "male_benef": demography["male_benef"],
        }
        for key, value in received_items.items():
            row[key] = value
        excel = excel._append(row, ignore_index=True)
    return excel


def main():
    entries = DataTable.objects.filter(
        project__name="US_UKR22_SV_007", category__name="Non-Food Items (NFI)"
    )
    excel = pd.DataFrame()
    excel = load_data(entries, excel)
    file_name = "output.xlsx"
    excel.to_excel(file_name, index=False, engine="openpyxl")


if __name__ == "__main__":
    main()
