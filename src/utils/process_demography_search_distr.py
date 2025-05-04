import os
import django
import pandas as pd

# django init
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "volunteer_reports.settings")
django.setup()

from search_distr.models import Person, Month, Region, Settlement, Distribution


def main():
    persons = Person.objects.all()
    total = len(persons)
    demography_qty = {
        "female_0_4": 0,
        "male_0_4": 0,
        "female_5_17": 0,
        "male_5_17": 0,
        "female_18_59": 0,
        "male_18_59": 0,
        "female_60plus": 0,
        "male_60plus": 0,
    }
    for p in persons:
        if p.gender == "w":
            if p.age < 5:
                demography_qty["female_0_4"] += 1
            if p.age >= 5 and p.age < 18:
                demography_qty["female_5_17"] += 1
            if p.age >= 18 and p.age < 60:
                demography_qty["female_18_59"] += 1
            if p.age >= 60:
                demography_qty["female_60plus"] += 1
        else:
            if p.age < 5:
                demography_qty["male_0_4"] += 1
            if p.age >= 5 and p.age < 18:
                demography_qty["male_5_17"] += 1
            if p.age >= 18 and p.age < 60:
                demography_qty["male_18_59"] += 1
            if p.age >= 60:
                demography_qty["male_60plus"] += 1
    for key, value in demography_qty.items():
        print(f"{key}: {round((value/total) * 100, 2)}%")


if __name__ == "__main__":
    main()
