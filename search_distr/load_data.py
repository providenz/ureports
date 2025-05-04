import os
import django
import pandas as pd

# django init
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "volunteer_reports.settings")
django.setup()

from search_distr.models import Person, Month, Region, Settlement, Distribution
from utils.custom_django_functions import get_or_create_object


def get_general_data(input_path):
    data_dict = {}
    try:
        df = pd.read_excel(input_path)

        region = df.iloc[4, 2]
        district = df.iloc[5, 2]
        community = df.iloc[6, 2]
        settlement = df.iloc[7, 2]
        date = df.iloc[1, 4]

        data_dict["region"] = region.strip()
        data_dict["district"] = district.strip()
        data_dict["community"] = community.strip()
        data_dict["settlement"] = settlement.strip()
        data_dict["date"] = date

        return data_dict
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def process_xlsx(input_path):
    general = get_general_data(input_path)
    region = get_or_create_object(Region, name=general["region"])
    settlement = get_or_create_object(
        Settlement,
        region=region,
        name=general["settlement"],
        community=general["community"],
        district=general["district"],
    )

    date = pd.to_datetime(general["date"], errors="coerce")
    month = get_or_create_object(Month, month=date.month, year=date.year)

    df = pd.read_excel(input_path, skiprows=13)
    for index, row in df.iterrows():
        if pd.isna(row["Вік/ Age"]):
            age = 0
        else:
            age = row["Вік/ Age"]
        if pd.isna(row["Телефон/ Phone"]):
            phone = "-"
        else:
            phone = "+380" + str(int(float(row["Телефон/ Phone"])))
        if pd.isna(row["Прізвище та ім’я /Name and surname"]):
            name = 0
        else:
            name = row["Прізвище та ім’я /Name and surname"]
        if pd.isna(row["Стать (Ч/Ж) /Gender"]):
            gender = "-"
        else:
            gender = row["Стать (Ч/Ж) /Gender"]
        if pd.isna(row["Адреса/ Address"]):
            address = "-"
        else:
            address = row["Адреса/ Address"]
        person = get_or_create_object(
            Person,
            name=name,
            address=address,
            phone=phone,
            age=age,
            gender=gender,
            settlement=settlement,
        )
        distribution = get_or_create_object(Distribution, person=person, month=month)
        print(f"Created distribution {distribution}")

    return True


def process_folder(input_folder):
    processed = 0
    skipped = 0

    for filename in os.listdir(input_folder):
        # Skip files that start with "~$"
        if filename.startswith("~$"):
            skipped += 1
            continue

        input_path = os.path.join(input_folder, filename)

        if os.path.isdir(input_path):
            if process_folder(input_path):
                processed += 1
            else:
                skipped += 1
        elif filename.lower().endswith((".xlsx",)):
            if process_xlsx(input_path):
                processed += 1
            else:
                skipped += 1

    return processed, skipped


def main():
    input_folder = "C:/Users/User/Desktop/U-Saved/Report"
    process_folder(input_folder)


if __name__ == "__main__":
    main()
