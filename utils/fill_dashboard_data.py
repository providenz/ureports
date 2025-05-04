import os
import django
import json
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "volunteer_reports.settings")
django.setup()

from reports.models import Project, Category, Dashboard, UpdateDashboard
from data_tables.models import DataTable, geojson_oblasts_names
from activity_map.models import Place


def main():
    projects = Project.objects.all()
    for project in projects:
        categories = project.categories.all()
        for category in categories:
            data_entries = DataTable.objects.filter(project=project, category=category)
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

            for i in data_entries:
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
                try:
                    pwd_counter += int(demography["female_PWD"]) + int(
                        demography["male_PWD"]
                    )
                except:
                    pwd_counter = 0

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


if __name__ == "__main__":
    main()
