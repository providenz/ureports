import os
import django
import random
import re
import pandas as pd
import json
from django.contrib.gis.geos import GEOSGeometry

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "volunteer_reports.settings")
django.setup()

from django.core.files import File
from reports.models import Project, Category
from data_tables.models import DataTable
from activity_map.models import Place, Marker
from accounts.models import CustomUser


def add_photo_to_db(base_dir, place_data, db_data):
    date_pattern = r"\d{4}-\d{2}-\d{2}"
    donors = CustomUser.objects.filter(is_superuser=False)
    bread_category = Category.objects.get(name="Bread Distribution")
    for city_folder in os.listdir(os.path.join(base_dir)):
        for photo_file in os.listdir(os.path.join(base_dir, city_folder)):
            for_data_name = photo_file.replace(" ", "_")
            try:
                gender = for_data_name.split("_")[1]
                age = for_data_name.split("_")[2]
                try:
                    age = int(age)
                except Exception:
                    age = random.choice(range(80))
                if gender not in ["female", "male"]:
                    gender = random.choice(["female", "male"])
                print(gender, age)
            except Exception as e:
                print(f"age or gender Error {e}")
                continue
            photo_path = os.path.join(base_dir, city_folder, photo_file)
            date_match = re.search(date_pattern, photo_file)
            if date_match:
                date = date_match.group()
            else:
                print(f"Error with file {photo_path}")
                continue
            with open(photo_path, "rb") as photo:
                donor = random.choice(donors)
                donor_projects = donor.donated_projects.all()
                if donor_projects:
                    chosen_projects = random.choice(donor_projects)
                    random_place = normalize_place_data(random.choice(place_data))
                    try:
                        place_instance = Place.objects.get(
                            oblast=random_place["oblast"],
                            rayon=random_place["rayon"],
                            gromada=random_place["gromada"],
                            settlement=random_place["settlement"],
                        )
                    except Exception:
                        place_instance = Place(
                            oblast=random_place["oblast"],
                            rayon=random_place["rayon"],
                            gromada=random_place["gromada"],
                            settlement=random_place["settlement"],
                        )
                        place_instance.save()
                    random_db_data = random.choice(db_data)
                    received_items, demography = normalize_db_data(random_db_data)
                    data_table_instance = DataTable(
                        project=chosen_projects,
                        category=bread_category,
                        photo=File(photo, name=photo_file),
                        gender=gender,
                        age=age,
                        date=date,
                        place=place_instance,
                        demography=demography,
                        received_items=received_items,
                    )
                    data_table_instance.save()


def get_place_data(path):
    try:
        data = pd.read_excel(path)
        place_data = []
        for index, row in data.iterrows():
            place_dict = {
                "oblast": row["Oblast"],
                "rayon": row["Rayon"],
                "hromada": row["Hromada"],
                "settlement": row["Settlement"],
            }
            place_data.append(place_dict)
        return place_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def normalize_place_data(place):
    return {
        "oblast": place["oblast"].split("_")[0].replace(" ", ""),
        "rayon": place["rayon"].split("_")[0].replace(" ", ""),
        "gromada": (place["hromada"].split("_")[0]).replace(" ", ""),
        "settlement": (place["settlement"].split("_")[0]).replace(" ", ""),
    }


def get_db_data(path):
    try:
        data = pd.read_excel(path)
        data.fillna(0, inplace=True)
        db_data = []
        for index, row in data.iterrows():
            db_dict = {
                "activity": row["activity"],
                "unit": row["unit"],
                "benef": row["benef"],
                "female_benef": row["female_benef"],
                "female_0_4": row["female_0_4"],
                "female_5_17": row["female_5_17"],
                "female_18_59": row["female_18_59"],
                "female_PWD": row["female_PWD"],
                "female_60plus": row["female_60plus"],
                "male_benef": row["male_benef"],
                "male_0_4": row["male_0_4"],
                "male_5_17": row["male_5_17"],
                "male_18_59": row["male_18_59"],
                "male_60plus": row["male_60plus"],
                "male_PWD": row["male_PWD"],
                "male_IDP": row["male_IDP"],
                "female_IDP": row["female_IDP"],
                "flag_IDP": row["flag_IDP"],
                "flag_PWD": row["flag_PWD"],
            }
            db_data.append(db_dict)
        return db_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def normalize_db_data(row):
    demography = {
        "female_benef": int(row["female_benef"]),
        "female_0_4": int(row["female_0_4"]),
        "female_5_17": int(row["female_5_17"]),
        "female_18_59": int(row["female_18_59"]),
        "female_PWD": int(row["female_PWD"]),
        "female_60plus": int(row["female_60plus"]),
        "male_benef": int(row["male_benef"]),
        "male_0_4": int(row["male_0_4"]),
        "male_5_17": int(row["male_5_17"]),
        "male_18_59": int(row["male_18_59"]),
        "male_60plus": int(row["male_60plus"]),
        "male_PWD": int(row["male_PWD"]),
        "male_IDP": int(row["male_IDP"]),
        "female_IDP": int(row["female_IDP"]),
        "flag_IDP": int(row["flag_IDP"]),
        "flag_PWD": int(row["flag_PWD"]),
    }
    received_items = {
        "activity": row["activity"],
        "unit": row["unit"],
        "benef": row["benef"],
    }
    return json.dumps(received_items), json.dumps(demography)


def create_markers(settlement, distribution, lon, lat):
    place_instance = Place.objects.get(settlement=settlement)
    category_instance = Category.objects.get(name=distribution)
    project_instance = Project.objects.all()[0]
    location_point = GEOSGeometry(f"POINT({lat} {lon})")

    marker = Marker.objects.create(
        category=category_instance,  # Replace with your Category instance
        project=project_instance,  # Replace with your Project instance
        place=place_instance,  # Replace with your Place instance
        location=location_point,  # Assign the PointField
    )
    marker.save()


def change_received_bread_items():
    data_entries = DataTable.objects.all()
    for entry in data_entries:
        entry.received_items = json.dumps({"bread": random.choice(range(1, 5))})
        entry.save()


def main():
    create_markers(
        "Nikopol", "Bread Distribution", 47.58076261306955, 34.38054354816123
    )
    create_markers(
        "Nikopol", "Water Distribution", 47.58076261306955, 34.38054354816123
    )
    create_markers("Nikopol", "Hygiene", 47.58076261306955, 34.38054354816123)


if __name__ == "__main__":
    main()
