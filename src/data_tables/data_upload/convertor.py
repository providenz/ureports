import json

import pandas as pd
import numpy as np
from datetime import datetime

from django.core.files.base import ContentFile

from reports.models import Project, Category, Dashboard, UpdateDashboard
from activity_map.models import Place, Marker
from data_tables.models import DataTable, geojson_oblasts_names
import zipfile
import os
from django.contrib.gis.geos import GEOSGeometry


class Convertor:
    def __init__(self, xlsx_file, zip_file):
        self.xlsx_file = xlsx_file
        self.zip_file = zip_file
        self.entries = []

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
        date = self.normalize_date(row["date"])
        if not date:
            errors["date"] = "Not valid date!"
        result["date"] = date
        try:
            project = Project.objects.get(name=row["project"])
            result["project"] = project
        except Project.DoesNotExist:
            errors["project"] = "Project not exist in DataBase!"
        try:
            category = Category.objects.get(name=row["category"])
            result["category"] = category
        except Category.DoesNotExist:
            errors["category"] = "Category not exist in Database!"
        photo_name = row["photo"]
        photo = self.photo_search(str(photo_name))
        result["photo"] = photo
        gender = row["gender"]
        if gender.lower() not in ["male", "female"]:
            errors["gender"] = "Gender not found!"
        else:
            result["gender"] = gender.lower()
        age = row["age"]
        try:
            age = int(age)
            result["age"] = age
        except Exception as e:
            errors["age"] = f"Error with age {age}: {e}"
        oblast = row["oblast"]
        rayon = row["rayon"]
        gromada = row["gromada"]
        settlement = row["settlement"]

        if not np.nan in [oblast, rayon, gromada, settlement]:
            result["place"] = {
                "oblast": oblast,
                "rayon": rayon,
                "gromada": gromada,
                "settlement": settlement,
            }
        else:
            errors["place"] = "Wrong place data!"
        latitude = row["latitude"]
        longitude = row["longitude"]
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            result["coords"] = (latitude, longitude)
        except Exception as e:
            errors["coords"] = f"Error with coordinates: {e}"

        demography = {}
        try:
            demography["benef"] = row["benef"]
            demography["female_0_4"] = row["female_0_4"]
            demography["female_5_17"] = row["female_5_17"]
            demography["female_18_59"] = row["female_18_59"]
            demography["female_60plus"] = row["female_60plus"]
            demography["male_0_4"] = row["male_0_4"]
            demography["male_5_17"] = row["male_5_17"]
            demography["male_18_59"] = row["male_18_59"]
            demography["male_60plus"] = row["male_60plus"]
            demography["male_PWD"] = row["male_pwd"]
            demography["female_PWD"] = row["female_pwd"]
            demography["female_benef"] = row["female_benef"]
            demography["male_benef"] = row["male_benef"]
            result["demography"] = demography
        except Exception as e:
            print(e)
        for key, value in demography.items():
            if value == np.nan:
                demography[key] = 0
        received_items = {}
        for column_name, column_value in row[25:].items():
            try:
                column_value = int(column_value)
                if column_value != 0:
                    received_items[column_name] = column_value
                else:
                    continue
            except:
                continue
        result["received_items"] = received_items

        if errors:
            print(f"Failed row: {index}...")
            print(errors)

            errors["index"] = index
            return "errors", errors
        else:
            print(f"Success row: {index}")
            return "success", result

    def normalize_date(self, date_obj):
        formats = ["%d.%m.%Y", "%d-%m-%Y", "%Y/%m/%d"]
        for fmt in formats:
            try:
                formatted_date = datetime.strftime(date_obj, fmt)
                return datetime.strptime(formatted_date, fmt).date()
            except ValueError:
                pass

        return None

    def photo_search(self, photo_name):
        if photo_name == np.nan:
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
            places = Place.objects.filter(settlement=entry["place"]["settlement"])

            if places.exists():
                place = places.first()
            else:
                place = Place.objects.create(
                    oblast=entry["place"]["oblast"],
                    rayon=entry["place"]["rayon"],
                    gromada=entry["place"]["gromada"],
                    settlement=entry["place"]["settlement"],
                )
                place.save()
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
            lat = coords[0]
            lon = coords[1]
            location_point = GEOSGeometry(f"POINT({lon} {lat})")

            try:
                marker = Marker.objects.get(
                    place=place, category=category, project=project
                )
            except Marker.DoesNotExist:
                marker = Marker.objects.create(
                    category=category,
                    project=project,
                    place=place,
                    location=location_point,
                )
                marker.save()
            create_entries += 1
            print(f"Created instanse {create_entries}/{data_len}...")
        return create_entries

    def update_dashboard(self, dashboard):
        upds = UpdateDashboard.objects.filter(dashboard=dashboard)
        total_benef = 0
        entry_counter = len(
            DataTable.objects.filter(
                project=dashboard.project, category=dashboard.category
            )
        )
        female_counter = 0
        male_counter = 0
        child_counter = 0
        over_60_counter = 0
        pwd_counter = 0
        total_qty = 0
        male_60plus = 0
        male_18_59 = 0
        male_5_17 = 0
        male_0_4 = 0
        male_18_59 = 0
        female_60plus = 0
        female_18_59 = 0
        female_5_17 = 0
        female_0_4 = 0
        female_18_59 = 0
        region_stats = {}
        received_items_stats = {}
        region_stats_list = []
        for upd in upds:
            total_benef += upd.total_benef
            female_counter += upd.females
            male_counter += upd.males
            child_counter += upd.children
            over_60_counter += upd.over_60
            pwd_counter += upd.pwds
            total_qty += upd.total_qty
            male_60plus += upd.male_60plus
            male_18_59 += upd.male_18_59
            male_5_17 += upd.male_5_17
            male_0_4 += upd.male_0_4
            male_18_59 += upd.male_18_59
            female_60plus += upd.female_60plus
            female_18_59 += upd.female_18_59
            female_5_17 += upd.female_5_17
            female_0_4 += upd.female_0_4
            female_18_59 += upd.female_18_59

            for upd_region in upd.region_stats:
                if not upd_region["name"] in region_stats.keys():
                    region_stats[upd_region["name"]] = {
                        "name": upd_region["name"],
                        "oblast": geojson_oblasts_names[upd_region["name"]],
                        "settlements": 0,
                    }
                region_stats[upd_region["name"]]["settlements"] += upd_region[
                    "settlements"
                ]
            for key, value in upd.received_items_stats.items():
                if not key in received_items_stats.keys():
                    received_items_stats[key] = 0
                received_items_stats[key] += value
        for key, value in region_stats.items():
            region_stats_list.append(value)
        dashboard.total_benef = total_benef
        dashboard.avg_people_in_family = (
            round(total_benef / entry_counter, 2) if entry_counter != 0 else 0
        )
        dashboard.female_percent = (
            round((female_counter / total_benef) * 100, 2) if total_benef != 0 else 0
        )
        dashboard.male_percent = (
            round((male_counter / total_benef) * 100, 2) if total_benef != 0 else 0
        )
        dashboard.children_percent = (
            round((child_counter / total_benef) * 100, 2) if total_benef != 0 else 0
        )
        dashboard.over_60_percent = (
            round((over_60_counter / total_benef) * 100, 2) if total_benef != 0 else 0
        )
        dashboard.pwd_percent = (
            round((pwd_counter / total_benef) * 100, 2) if total_benef != 0 else 0
        )
        dashboard.total_qty = total_qty
        dashboard.male_60plus = (
            round((male_60plus / total_benef) * 100, 2) if total_benef != 0 else 0
        )
        dashboard.male_18_59 = (
            round((male_18_59 / total_benef) * 100, 2) if total_benef != 0 else 0
        )
        dashboard.male_5_17 = (
            round((male_5_17 / total_benef) * 100, 2) if total_benef != 0 else 0
        )
        dashboard.male_0_4 = (
            round((male_0_4 / total_benef) * 100, 2) if total_benef != 0 else 0
        )
        dashboard.female_60plus = (
            round((female_60plus / total_benef) * 100, 2) if total_benef != 0 else 0
        )
        dashboard.female_18_59 = (
            round((female_18_59 / total_benef) * 100, 2) if total_benef != 0 else 0
        )
        dashboard.female_5_17 = (
            round((female_5_17 / total_benef) * 100, 2) if total_benef != 0 else 0
        )
        dashboard.female_0_4 = (
            round((female_0_4 / total_benef) * 100, 2) if total_benef != 0 else 0
        )
        dashboard.region_stats = region_stats_list
        dashboard.received_items_stats = received_items_stats
        dashboard.save()

    def fill_dashboard(self):
        project = self.entries[0].project
        category = self.entries[0].category
        try:
            dashboard = Dashboard.objects.get(project=project, category=category)
            total_benef = 0
            entry_counter = 0
            female_counter = 0
            male_counter = 0
            child_counter = 0
            over_60_counter = 0
            pwd_counter = 0
            total_qty = 0
            male_60plus = 0
            male_18_59 = 0
            male_5_17 = 0
            male_0_4 = 0
            male_18_59 = 0
            female_60plus = 0
            female_18_59 = 0
            female_5_17 = 0
            female_0_4 = 0
            female_18_59 = 0
            region_stats = {}
            received_items_stats = {}

            already_settlements = []
            for i in self.entries:
                region = i.place.oblast
                if not region in region_stats.keys():
                    region_stats[region] = {
                        "name": region,
                        "oblast": geojson_oblasts_names[region],
                        "settlements": 0,
                    }
                settlement = i.place.settlement
                if not settlement in already_settlements:
                    region_stats[region]["settlements"] += 1
                    already_settlements.append(settlement)
                demography = json.loads(i.demography)
                received = json.loads(i.received_items)
                total_benef += int(demography["benef"])
                entry_counter += 1
                female_counter += int(demography["female_benef"])
                male_counter += int(demography["male_benef"])
                child_counter += (
                    int(demography["female_0_4"])
                    + int(demography["male_0_4"])
                    + int(demography["female_5_17"])
                    + int(demography["male_5_17"])
                )
                over_60_counter += int(demography["female_60plus"]) + int(
                    demography["male_60plus"]
                )
                pwd_counter += int(demography["female_PWD"]) + int(
                    demography["male_PWD"]
                )

                male_60plus += int(demography["male_60plus"])
                male_18_59 += int(demography["male_18_59"])
                male_5_17 += int(demography["male_5_17"])
                male_0_4 += int(demography["male_0_4"])
                female_60plus += int(demography["female_60plus"])
                female_5_17 += int(demography["female_5_17"])
                female_0_4 += int(demography["female_0_4"])
                female_18_59 += int(demography["female_18_59"])
                for key, value in received.items():
                    total_qty += int(value)
                    if not key in received_items_stats.keys():
                        received_items_stats[key] = 0
                    received_items_stats[key] += value
            region_stats_list = []
            for key, value in region_stats.items():
                region_stats_list.append(value)
            new_upd = UpdateDashboard.objects.create(
                dashboard=dashboard,
                total_benef=total_benef,
                females=female_counter,
                males=male_counter,
                children=child_counter,
                over_60=over_60_counter,
                pwds=pwd_counter,
                total_qty=total_qty,
                male_60plus=male_60plus,
                male_18_59=male_18_59,
                male_5_17=male_5_17,
                male_0_4=male_0_4,
                female_60plus=female_60plus,
                female_18_59=female_18_59,
                female_5_17=female_5_17,
                female_0_4=female_0_4,
                region_stats=region_stats_list,
                received_items_stats=received_items_stats,
            )
            new_upd.save()
            self.update_dashboard(dashboard)
        except Dashboard.DoesNotExist:
            total_benef = 0
            entry_counter = 0
            female_counter = 0
            male_counter = 0
            child_counter = 0
            over_60_counter = 0
            pwd_counter = 0
            total_qty = 0
            male_60plus = 0
            male_18_59 = 0
            male_5_17 = 0
            male_0_4 = 0
            male_18_59 = 0
            female_60plus = 0
            female_18_59 = 0
            female_5_17 = 0
            female_0_4 = 0
            female_18_59 = 0
            region_stats = {}
            received_items_stats = {}

            already_settlements = []

            for i in self.entries:
                region = i.place.oblast
                if not region in region_stats.keys():
                    region_stats[region] = {
                        "name": region,
                        "oblast": geojson_oblasts_names[region],
                        "settlements": 0,
                    }
                settlement = i.place.settlement
                if not settlement in already_settlements:
                    region_stats[region]["settlements"] += 1
                    already_settlements.append(settlement)
                demography = json.loads(i.demography)
                received = json.loads(i.received_items)
                total_benef += int(demography["benef"])
                entry_counter += 1
                female_counter += int(demography["female_benef"])
                male_counter += int(demography["male_benef"])
                child_counter += (
                    int(demography["female_0_4"])
                    + int(demography["male_0_4"])
                    + int(demography["female_5_17"])
                    + int(demography["male_5_17"])
                )
                over_60_counter += int(demography["female_60plus"]) + int(
                    demography["male_60plus"]
                )
                pwd_counter += int(demography["female_PWD"]) + int(
                    demography["male_PWD"]
                )

                male_60plus += int(demography["male_60plus"])
                male_18_59 += int(demography["male_18_59"])
                male_5_17 += int(demography["male_5_17"])
                male_0_4 += int(demography["male_0_4"])
                female_60plus += int(demography["female_60plus"])
                female_5_17 += int(demography["female_5_17"])
                female_0_4 += int(demography["female_0_4"])
                female_18_59 += int(demography["female_18_59"])
                for key, value in received.items():
                    total_qty += int(value)
                    if not key in received_items_stats.keys():
                        received_items_stats[key] = 0
                    received_items_stats[key] += value
            region_stats_list = []
            for key, value in region_stats.items():
                region_stats_list.append(value)
            dashboard = Dashboard.objects.create(
                project=project,
                category=category,
                total_benef=total_benef,
                avg_people_in_family=round(total_benef / entry_counter, 2)
                if entry_counter != 0
                else 0,
                female_percent=round((female_counter / total_benef) * 100, 2)
                if total_benef != 0
                else 0,
                male_percent=round((male_counter / total_benef) * 100, 2)
                if total_benef != 0
                else 0,
                children_percent=round((child_counter / total_benef) * 100, 2)
                if total_benef != 0
                else 0,
                over_60_percent=round((over_60_counter / total_benef) * 100, 2)
                if total_benef != 0
                else 0,
                pwd_percent=round((pwd_counter / total_benef) * 100, 2)
                if total_benef != 0
                else 0,
                total_qty=total_qty,
                male_60plus=round((male_60plus / total_benef) * 100, 2)
                if total_benef != 0
                else 0,
                male_18_59=round((male_18_59 / total_benef) * 100, 2)
                if total_benef != 0
                else 0,
                male_5_17=round((male_5_17 / total_benef) * 100, 2)
                if total_benef != 0
                else 0,
                male_0_4=round((male_0_4 / total_benef) * 100, 2)
                if total_benef != 0
                else 0,
                female_60plus=round((female_60plus / total_benef) * 100, 2)
                if total_benef != 0
                else 0,
                female_18_59=round((female_18_59 / total_benef) * 100, 2)
                if total_benef != 0
                else 0,
                female_5_17=round((female_5_17 / total_benef) * 100, 2)
                if total_benef != 0
                else 0,
                female_0_4=round((female_0_4 / total_benef) * 100, 2)
                if total_benef != 0
                else 0,
                region_stats=region_stats_list,
                received_items_stats=received_items_stats,
            )
            dashboard.save()
            upd = UpdateDashboard.objects.create(
                dashboard=dashboard,
                total_benef=total_benef,
                females=female_counter,
                males=male_counter,
                children=child_counter,
                over_60=over_60_counter,
                pwds=pwd_counter,
                total_qty=total_qty,
                male_60plus=male_60plus,
                male_18_59=male_18_59,
                male_5_17=male_5_17,
                male_0_4=male_0_4,
                female_60plus=female_60plus,
                female_18_59=female_18_59,
                female_5_17=female_5_17,
                female_0_4=female_0_4,
                region_stats=region_stats_list,
                received_items_stats=received_items_stats,
            )
            upd.save()
