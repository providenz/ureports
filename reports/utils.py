from data_tables.models import DataTable, geojson_oblasts_names
from reports.models import Dashboard, UpdateDashboard
from activity_map.models import Place


def get_total_dashboard(dashboards):
    entry_counter = len(DataTable.objects.all())
    total_benef = 0
    total_qty = 0
    females = 0
    males = 0
    children = 0
    over_60 = 0
    female_0_4 = 0
    female_5_17 = 0
    female_18_59 = 0
    female_60plus = 0
    male_0_4 = 0
    male_5_17 = 0
    male_18_59 = 0
    male_60plus = 0
    pwds = 0
    m_f_total = 0
    received_items = {}
    region_stats = {}
    region_stats_list = []
    for dash in dashboards:
        total_qty += dash.total_qty
        for key, value in dash.received_items_stats.items():
            if key in received_items.keys():
                received_items[key] += value
            else:
                received_items[key] = value
        for region in dash.region_stats:
            if not region["name"] in region_stats.keys():
                region_stats[region["name"]] = {
                    "name": region["name"],
                    "oblast": geojson_oblasts_names[region["name"]],
                    "settlements": 0,
                }
            region_stats[region["name"]]["settlements"] += region["settlements"]
        upds = UpdateDashboard.objects.filter(dashboard=dash)
        for upd in upds:
            total_benef += upd.total_benef
            m_f_total += upd.females + upd.males
            females += upd.females
            males += upd.males
            children += upd.children
            over_60 += upd.over_60
            pwds += upd.pwds
            female_0_4 += upd.female_0_4
            female_5_17 += upd.female_5_17
            female_18_59 += upd.female_18_59
            female_60plus += upd.female_60plus
            male_0_4 += upd.male_0_4
            male_5_17 += upd.male_5_17
            male_18_59 += upd.male_18_59
            male_60plus += upd.male_60plus
    for key, value in region_stats.items():
        region_stats_list.append(value)
    region_prepared = []
    total_place = len(Place.objects.all())
    for region in region_stats_list:
        obj = {
            "name": str(region["name"]),
            "oblast": region["oblast"],
            "coverage": round((int(region["settlements"]) / total_place) * 100, 2),
            "places": region["settlements"],
        }
        region_prepared.append(obj)
    sorted_items = dict(
        sorted(received_items.items(), key=lambda x: x[1], reverse=True)
    )
    sorted_region = sorted(region_prepared, key=lambda x: x["coverage"], reverse=True)

    return {
        "total_benef": total_benef,
        "female_percent": round((females / m_f_total) * 100, 2)
        if m_f_total != 0
        else 0,
        "male_percent": round((males / m_f_total) * 100, 2) if m_f_total != 0 else 0,
        "children_percent": round((children / total_benef) * 100, 2)
        if total_benef != 0
        else 0,
        "over_60_percent": round((over_60 / total_benef) * 100, 2)
        if total_benef != 0
        else 0,
        "pwd_percent": round((pwds / total_benef) * 100, 2) if total_benef != 0 else 0,
        "total_qty": total_qty,
        "male_60plus": round((male_60plus / total_benef) * 100, 2)
        if total_benef != 0
        else 0,
        "male_18_59": round((male_18_59 / total_benef) * 100, 2)
        if total_benef != 0
        else 0,
        "male_5_17": round((male_5_17 / total_benef) * 100, 2)
        if total_benef != 0
        else 0,
        "male_0_4": round((male_0_4 / total_benef) * 100, 2) if total_benef != 0 else 0,
        "female_60plus": round((female_60plus / total_benef) * 100, 2)
        if total_benef != 0
        else 0,
        "female_18_59": round((female_18_59 / total_benef) * 100, 2)
        if total_benef != 0
        else 0,
        "female_5_17": round((female_5_17 / total_benef) * 100, 2)
        if total_benef != 0
        else 0,
        "female_0_4": round((female_0_4 / total_benef) * 100, 2)
        if total_benef != 0
        else 0,
        "region_stats": sorted_region,
        "received_items_stats": sorted_items,
    }
