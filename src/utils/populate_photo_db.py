import os
import django
import random
import re
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "volunteer_reports.settings")
django.setup()

from django.core.files import File
from reports.models import Project, DistributionPhoto, Category
from accounts.models import CustomUser


def add_photo_to_db(base_dir, excel_data):
    date_pattern = r"\d{4}-\d{2}-\d{2}"
    donors = CustomUser.objects.filter(is_superuser=False)
    bread_category = Category.objects.get(name="Bread Distribution")
    for city_folder in os.listdir(os.path.join(base_dir)):
        for photo_file in os.listdir(os.path.join(base_dir, city_folder)):
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
                    random_excel_data = random.choice(excel_data)
                    oblast, place = normalize_excel_data(
                        random_excel_data[0], random_excel_data[1]
                    )
                    photo_instance = DistributionPhoto(
                        project=chosen_projects,
                        category=bread_category,
                        photo=File(photo, name=photo_file),
                        date=date,
                        city=place,
                        region=oblast,
                    )
                    photo_instance.save()


def get_excel_data(excel_file_path):
    df = pd.read_excel(os.path.join(excel_file_path))
    data_list = df.values.tolist()
    return data_list


def normalize_excel_data(oblast, place):
    oblast = oblast.split("_")[0]
    place = "_".join(place.split("_")[:1])
    return oblast, place


def main():
    data = get_excel_data("C:/Users/User/Desktop/bread_places.xlsx")
    add_photo_to_db("C:/Users/User/Desktop/blured_photos/bread", data)


if __name__ == "__main__":
    main()
