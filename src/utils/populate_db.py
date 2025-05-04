import os
import django
import random
from faker import Faker

# Инициализация Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "volunteer_reports.settings")
django.setup()

from accounts.models import CustomUser
from reports.models import Project, DistributionPhoto, Category
from django.core.files import File

fake = Faker()


def add_photos_to_db(photo_folder_path):
    donors = CustomUser.objects.filter(is_superuser=False)
    all_categories = list(Category.objects.all())

    all_photos = os.listdir(photo_folder_path)
    random.shuffle(
        all_photos
    )  # Перемешиваем список фото, чтобы распределить их случайным образом

    for photo_file in all_photos:
        photo_path = os.path.join(photo_folder_path, photo_file)
        with open(photo_path, "rb") as photo:
            # Выбираем случайного донора и из его проектов случайный проект
            donor = random.choice(donors)
            donor_projects = donor.donated_projects.all()
            if donor_projects:  # Проверяем, есть ли у донора проекты
                chosen_project = random.choice(donor_projects)
                random_category = random.choice(all_categories)

                # Создаем новую фотографию в базе данных
                photo_instance = DistributionPhoto(
                    project=chosen_project,
                    category=random_category,
                    photo=File(photo, name=photo_file),
                    date=fake.date_between(start_date="-1y", end_date="today"),
                    city=fake.city(),
                )
                photo_instance.save()


if __name__ == "__main__":
    photo_folder_path = "test_photo"
    add_photos_to_db(photo_folder_path)
