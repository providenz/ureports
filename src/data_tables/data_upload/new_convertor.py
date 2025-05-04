import os
import json
import zipfile
import pandas as pd
import numpy as np

from datetime import datetime
from collections import defaultdict
from django.core.files.base import ContentFile
from django.contrib.gis.geos import GEOSGeometry

from reports.models import Project, Category, Dashboard, UpdateDashboard
from activity_map.models import Place, Marker
from data_tables.models import DataTable, geojson_oblasts_names
from utils.custom_django_functions import get_or_create_object


class Convertor:
    def __init__(self, xlsx_file, zip_file):
        self.xlsx_file = xlsx_file
        self.zip_file = zip_file
        self.entries = []
        self.new_places = []

    def extract_data_from_excel(self):
        data = pd.read_excel(self.xlsx_file)
        result = {"data": [], "errors": []}

        for index, row in data.iterrows():
            status, normalize_data = self.validate_row(index, row)
            if status == "errors":
                result["errors"].append(normalize_data)
            else:
                result["data"].append(normalize_data)
        return result

    def validate_row(self, index, row):
        print(f"Work with row {index}...")
        result = {}
        errors = {}
        result["date"] = self.validate_date(row["date"], errors)

        result["project"] = self.get_object_or_error(
            model=Project,
            value=row["project"],
            field="name",
            errors=errors,
            model_name="Project",
        )
        result["category"] = self.get_object_or_error(
            model=Category,
            value=row["category"],
            field="name",
            errors=errors,
            model_name="Category",
        )
        result["photo"] = self.photo_search(str(row["photo"]))
        result["gender"] = self.validate_gender(row["gender"], errors)
        result["age"] = self.validate_integer(row["age"], "age", errors)
        result["place"] = self.validate_place(
            row["oblast"], row["rayon"], row["gromada"], row["settlement"], errors
        )
        result["coords"] = self.validate_coordinates(
            row["latitude"], row["longitude"], errors
        )
        result["demography"] = self.process_demography(row)
        result["received_items"] = self.process_received_items(row)

        if errors:
            print(f"Failed row: {index}... {errors}")
            errors["index"] = index
            return "errors", errors
        else:
            print(f"Success row: {index}")
            return "success", result

    def get_object_or_error(self, model, value, field, errors, model_name):
        try:
            obj = model.objects.get(**{field: value})
            return obj
        except model.DoesNotExist:
            errors[field] = f"{model_name} not exist in Database!"
            return None


    def validate_date(self, date_obj, errors):
        formats = ["%d.%m.%Y", "%d-%m-%Y", "%Y/%m/%d"]
        for fmt in formats:
            try:
                formatted_date = datetime.strftime(date_obj, fmt)
                return datetime.strptime(formatted_date, fmt).date()
            except ValueError:
                pass
        errors["date"] = "Not valid date!"
        return None

    def validate_gender(self, gender, errors):
        if gender not in ["male", "female"]:
            errors["gender"] = "Gender not found!"
            return None
        return gender

    def validate_integer(self, value, field, errors):
        try:
            return int(value)
        except Exception as e:
            errors[field] = f"Error with {field} {value}: {e}"
            return None

    def validate_place(self, oblast, rayon, gromada, settlement, errors):
        if all(field is not np.nan for field in [oblast, rayon, gromada, settlement]):
            return {
                "oblast": oblast,
                "rayon": rayon,
                "gromada": gromada,
                "settlement": settlement,
            }
        else:
            errors["place"] = "Wrong place data!"
            return None

    def validate_coordinates(self, latitude, longitude, errors):
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            return (latitude, longitude)
        except Exception as e:
            errors["coords"] = f"Error with coordinates: {e}"
            return None

    def process_demography(self, row):
        demography_keys = [
            "benef",
            "female_0_4",
            "female_5_17",
            "female_18_59",
            "female_60plus",
            "male_0_4",
            "male_5_17",
            "male_18_59",
            "male_60plus",
            "male_PWD",
            "female_PWD",
            "female_benef",
            "male_benef",
        ]
        demography = {
            key: self.validate_integer(row[key], key, {}) for key in demography_keys
        }
        return {
            key: value if value is not None else 0 for key, value in demography.items()
        }

    def process_received_items(self, row):
        received_items = {
            key: self.validate_integer(row[key], key, {})
            for key, value in row[25:].items()
        }
        return {key: value for key, value in received_items.items() if value != 0}

    def photo_search(self, photo_name):
        if pd.isna(photo_name):
            return None
        print(f"Search for photo {photo_name}...")
        with zipfile.ZipFile(self.zip_file, "r") as zip_ref:
            file_list = zip_ref.namelist()
            filename_to_search = os.path.basename(photo_name)
            matching_files = [
                file
                for file in file_list
                if os.path.basename(file) == filename_to_search
            ]
            if matching_files:
                file_data = zip_ref.read(matching_files[0])
                file = ContentFile(file_data, photo_name)
                print(f"Success for photo {photo_name}!")
                return file
            else:
                return None

    def create_instances(self, data):
        print(f"Create instances start...")
        create_entries = 0
        data_len = len(data)
        for entry in data:
            try:
                place = Place.objects.get(
                    settlement=entry["place"]["settlement"],
                    oblast=entry["place"]["oblast"],
                    rayon=entry["place"]["rayon"],
                    gromada=entry["place"]["gromada"],
                )
            except Place.DoesNotExist:
                place = Place.objects.create(
                    settlement=entry["place"]["settlement"],
                    oblast=entry["place"]["oblast"],
                    rayon=entry["place"]["rayon"],
                    gromada=entry["place"]["gromada"],
                )
                self.new_places.append(place)
            received_items = json.dumps(entry["received_items"])
            demography = json.dumps(entry["demography"])
            project = entry["project"]
            category = entry["category"]
            photo = entry["photo"]
            coords = entry["coords"]
            date = entry["date"]
            gender = entry["gender"]
            age = entry["age"]
            data_table = DataTable.objects.create(
                date=date,
                place=place,
                received_items=received_items,
                demography=demography,
                project=project,
                category=category,
                photo=photo,
                gender=gender,
                age=age,
            )
            self.entries.append(data_table)
            create_entries += 1
            print(f"Created instance {create_entries}/{data_len}...")
            location_point = GEOSGeometry(f"POINT({coords[1]} {coords[0]})")
            get_or_create_object(
                Marker,
                place=place,
                category=category,
                project=project,
                location=location_point,
            )
        return create_entries

    def update_dashboard(self, dashboard):
        upds = UpdateDashboard.objects.filter(dashboard=dashboard)
        total_benef = 0
        entry_counter = len(
            DataTable.objects.filter(
                project=dashboard.project, category=dashboard.category
            )
        )
        demographics_counters = defaultdict(int)
        region_stats = defaultdict(lambda: {"name": "", "oblast": "", "settlements": 0})
        received_items_stats = defaultdict(int)

        for upd in upds:
            total_benef += upd.total_benef
            demographics_counters["females"] += upd.females
            demographics_counters["males"] += upd.males
            demographics_counters["children"] += upd.children
            demographics_counters["over_60"] += upd.over_60
            demographics_counters["pwds"] += upd.pwds
            demographics_counters["total_qty"] += upd.total_qty

            demographics_counters["male_60plus"] += upd.male_60plus
            demographics_counters["male_18_59"] += upd.male_18_59
            demographics_counters["male_5_17"] += upd.male_5_17
            demographics_counters["male_0_4"] += upd.male_0_4
            demographics_counters["female_60plus"] += upd.female_60plus
            demographics_counters["female_18_59"] += upd.female_18_59
            demographics_counters["female_5_17"] += upd.female_5_17
            demographics_counters["female_0_4"] += upd.female_0_4

            for upd_region in upd.region_stats:
                region_stats[upd_region["name"]]["name"] = upd_region["name"]
                region_stats[upd_region["name"]]["oblast"] = geojson_oblasts_names[
                    upd_region["name"]
                ]
                region_stats[upd_region["name"]]["settlements"] += upd_region[
                    "settlements"
                ]

            for key, value in upd.received_items_stats.items():
                received_items_stats[key] += value

        dashboard.total_benef = total_benef
        dashboard.avg_people_in_family = (
            round(total_benef / entry_counter, 2) if entry_counter != 0 else 0
        )
        dashboard.female_percent = (
            round((demographics_counters["females"] / total_benef) * 100, 2)
            if total_benef != 0
            else 0
        )
        dashboard.male_percent = (
            round((demographics_counters["males"] / total_benef) * 100, 2)
            if total_benef != 0
            else 0
        )
        dashboard.children_percent = (
            round((demographics_counters["children"] / total_benef) * 100, 2)
            if total_benef != 0
            else 0
        )
        dashboard.over_60_percent = (
            round((demographics_counters["over_60"] / total_benef) * 100, 2)
            if total_benef != 0
            else 0
        )
        dashboard.pwd_percent = (
            round((demographics_counters["pwds"] / total_benef) * 100, 2)
            if total_benef != 0
            else 0
        )
        dashboard.total_qty = demographics_counters["total_qty"]

        for gender in ["male", "female"]:
            for age_group in ["60plus", "18_59", "5_17", "0_4"]:
                key = f"{gender}_{age_group}"
                setattr(
                    dashboard,
                    key,
                    round((demographics_counters[key] / total_benef) * 100, 2)
                    if total_benef != 0
                    else 0,
                )

        dashboard.region_stats = list(region_stats.values())
        dashboard.received_items_stats = dict(received_items_stats)
        dashboard.save()

    def fill_dashboard(self):
        project = self.entries[0].project
        category = self.entries[0].category

        try:
            dashboard = Dashboard.objects.get(project=project, category=category)
            is_new_dashboard = False
        except Dashboard.DoesNotExist:
            dashboard = Dashboard.objects.create(
                project=project,
                category=category,
                total_benef=0,
                avg_people_in_family=0,
                female_percent=0,
                male_percent=0,
                children_percent=0,
                over_60_percent=0,
                pwd_percent=0,
                total_qty=0,
                male_60plus=0,
                male_18_59=0,
                male_5_17=0,
                male_0_4=0,
                female_60plus=0,
                female_18_59=0,
                female_5_17=0,
                female_0_4=0,
                region_stats=[],
                received_items_stats={},
            )
            is_new_dashboard = True

        demographics_counters = defaultdict(int)
        region_stats = defaultdict(lambda: {"name": "", "oblast": "", "settlements": 0})
        received_items_stats = defaultdict(int)
        already_settlements = set()
        total_qty = 0
        for entry in self.entries:
            region = entry.place.oblast
            if region not in region_stats:
                region_stats[region] = {
                    "name": region,
                    "oblast": geojson_oblasts_names[region],
                    "settlements": 0,
                }

            settlement = entry.place.settlement
            if settlement not in already_settlements:
                region_stats[region]["settlements"] += 1
                already_settlements.add(settlement)

            demography = json.loads(entry.demography)
            received = json.loads(entry.received_items)

            demographics_counters["benef"] += int(demography["benef"])
            demographics_counters["female_benef"] += int(demography["female_benef"])
            demographics_counters["male_benef"] += int(demography["male_benef"])
            demographics_counters["children"] += (
                int(demography["female_0_4"])
                + int(demography["male_0_4"])
                + int(demography["female_5_17"])
                + int(demography["male_5_17"])
            )
            demographics_counters["over_60"] += int(demography["female_60plus"]) + int(
                demography["male_60plus"]
            )
            demographics_counters["PWD"] += int(demography["female_PWD"]) + int(
                demography["male_PWD"]
            )

            demographics_counters["male_60plus"] += int(demography["male_60plus"])
            demographics_counters["male_18_59"] += int(demography["male_18_59"])
            demographics_counters["male_5_17"] += int(demography["male_5_17"])
            demographics_counters["male_0_4"] += int(demography["male_0_4"])
            demographics_counters["female_60plus"] += int(demography["female_60plus"])
            demographics_counters["female_18_59"] += int(demography["female_18_59"])
            demographics_counters["female_5_17"] += int(demography["female_5_17"])
            demographics_counters["female_0_4"] += int(demography["female_0_4"])

            for key, value in received.items():
                received_items_stats[key] += int(value)
                total_qty += int(value)

        print(total_qty)
        region_stats_list = list(region_stats.values())
        new_upd = UpdateDashboard.objects.create(
            dashboard=dashboard,
            total_benef=demographics_counters["benef"],
            females=demographics_counters["female_benef"],
            males=demographics_counters["male_benef"],
            children=demographics_counters["children"],
            over_60=demographics_counters["over_60"],
            pwds=demographics_counters["PWD"],
            total_qty=total_qty,
            male_60plus=demographics_counters["male_60plus"],
            male_18_59=demographics_counters["male_18_59"],
            male_5_17=demographics_counters["male_5_17"],
            male_0_4=demographics_counters["male_0_4"],
            female_60plus=demographics_counters["female_60plus"],
            female_18_59=demographics_counters["female_18_59"],
            female_5_17=demographics_counters["female_5_17"],
            female_0_4=demographics_counters["female_0_4"],
            region_stats=region_stats_list,
            received_items_stats=received_items_stats,
        )
        new_upd.save()

        if is_new_dashboard:
            dashboard.total_benef = demographics_counters["benef"]
            dashboard.total_qty = total_qty
            entry_counter = len(self.entries)
            dashboard.avg_people_in_family = (
                round(demographics_counters["benef"] / entry_counter, 2)
                if entry_counter != 0
                else 0
            )
            dashboard.female_percent = (
                round(
                    (demographics_counters["female_benef"] / dashboard.total_benef)
                    * 100,
                    2,
                )
                if dashboard.total_benef != 0
                else 0
            )
            dashboard.male_percent = (
                round(
                    (demographics_counters["male_benef"] / dashboard.total_benef) * 100,
                    2,
                )
                if dashboard.total_benef != 0
                else 0
            )
            dashboard.children_percent = (
                round(
                    (demographics_counters["children"] / dashboard.total_benef) * 100, 2
                )
                if dashboard.total_benef != 0
                else 0
            )
            dashboard.over_60_percent = (
                round(
                    (demographics_counters["over_60"] / dashboard.total_benef) * 100, 2
                )
                if dashboard.total_benef != 0
                else 0
            )
            dashboard.pwd_percent = (
                round((demographics_counters["PWD"] / dashboard.total_benef) * 100, 2)
                if dashboard.total_benef != 0
                else 0
            )
            dashboard.total_qty = demographics_counters["total_qty"]

            for gender in ["male", "female"]:
                for age_group in ["60plus", "18_59", "5_17", "0_4"]:
                    key = f"{gender}_{age_group}"
                    setattr(
                        dashboard,
                        key,
                        round(
                            (demographics_counters[key] / dashboard.total_benef) * 100,
                            2,
                        )
                        if dashboard.total_benef != 0
                        else 0,
                    )

            dashboard.region_stats = region_stats_list
            dashboard.received_items_stats = dict(received_items_stats)
            dashboard.save()
        else:
            self.update_dashboard(dashboard)
