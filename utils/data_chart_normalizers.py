import json

# import random


class DataChartNormalizer:
    def __init__(self, data_entries):
        self.data_entries = data_entries

    def get_normalized_data(self):
        global_demography_category = {}
        global_demography_category_oblasts = {}
        global_age_category = {}
        global_gender = {"male": 0, "female": 0}
        family_oblast_buffer = {}
        family_oblast = {}
        family_category_buffer = {}
        family_category = {}
        pwd_oblast_buffer = {}
        pwd_oblast = {}
        pwd_category_buffer = {}
        pwd_category = {}
        children_oblast_buffer = {}
        children_oblast = {}
        children_category_buffer = {}
        children_category = {}
        time_benef = {}
        time_benef_category = {}
        for entry in self.data_entries:
            demography = json.loads(entry.demography)
            date = entry.date.strftime("%B-%Y")
            oblast = entry.place.oblast
            total_benef = int(demography["benef"])
            category = entry.category.name
            if global_demography_category.get(category):
                global_demography_category[category] += total_benef
            else:
                global_demography_category[category] = total_benef
            if global_demography_category_oblasts.get(oblast):
                if global_demography_category_oblasts.get(oblast).get(category):
                    global_demography_category_oblasts[oblast][category] += total_benef
                else:
                    global_demography_category_oblasts[oblast][category] = total_benef
            else:
                global_demography_category_oblasts[oblast] = {category: total_benef}

            if global_age_category.get(category):
                global_age_category[category]["0_4"] += (
                    demography["female_0_4"] + demography["male_0_4"]
                )
                global_age_category[category]["5_17"] += (
                    demography["female_5_17"] + demography["male_5_17"]
                )
                global_age_category[category]["18_59"] += (
                    demography["female_18_59"] + demography["male_18_59"]
                )
                global_age_category[category]["60plus"] += (
                    demography["female_60plus"] + demography["male_60plus"]
                )
            else:
                global_age_category[category] = {}
                global_age_category[category]["0_4"] = (
                    demography["female_0_4"] + demography["male_0_4"]
                )
                global_age_category[category]["5_17"] = (
                    demography["female_5_17"] + demography["male_5_17"]
                )
                global_age_category[category]["18_59"] = (
                    demography["female_18_59"] + demography["male_18_59"]
                )
                global_age_category[category]["60plus"] = (
                    demography["female_60plus"] + demography["male_60plus"]
                )

            if family_oblast_buffer.get(oblast):
                family_oblast_buffer[oblast]["qty"] += 1
                family_oblast_buffer[oblast]["benef"] += total_benef
            else:
                family_oblast_buffer[oblast] = {
                    "qty": 1,
                    "benef": total_benef,
                }
            if family_category_buffer.get(category):
                family_category_buffer[category]["qty"] += 1
                family_category_buffer[category]["benef"] += total_benef
            else:
                family_category_buffer[category] = {
                    "qty": 1,
                    "benef": total_benef,
                }
            if pwd_oblast_buffer.get(oblast):
                pwd_oblast_buffer[oblast] += (
                    demography["female_PWD"] + demography["male_PWD"]
                )
            else:
                pwd_oblast_buffer[oblast] = (
                    demography["female_PWD"] + demography["male_PWD"]
                )
            if pwd_category_buffer.get(category):
                pwd_category_buffer[category] += (
                    demography["female_PWD"] + demography["male_PWD"]
                )
            else:
                pwd_category_buffer[category] = (
                    demography["female_PWD"] + demography["male_PWD"]
                )
            if children_oblast_buffer.get(oblast):
                children_oblast_buffer[oblast]["benef"] += (
                    demography["female_0_4"]
                    + demography["female_5_17"]
                    + demography["male_0_4"]
                    + demography["male_5_17"]
                )
                children_oblast_buffer[oblast]["qty"] += 1
            else:
                children_oblast_buffer[oblast] = {
                    "qty": 1,
                    "benef": demography["female_0_4"]
                    + demography["female_5_17"]
                    + demography["male_0_4"]
                    + demography["male_5_17"],
                }

            if children_category_buffer.get(category):
                children_category_buffer[category]["benef"] += (
                    demography["female_0_4"]
                    + demography["female_5_17"]
                    + demography["male_0_4"]
                    + demography["male_5_17"]
                )
                children_category_buffer[category]["qty"] += 1
            else:
                children_category_buffer[category] = {
                    "qty": 1,
                    "benef": demography["female_0_4"]
                    + demography["female_5_17"]
                    + demography["male_0_4"]
                    + demography["male_5_17"],
                }
            if time_benef.get(oblast):
                if time_benef[oblast].get(date):
                    time_benef[oblast][date] += total_benef
                else:
                    time_benef[oblast][date] = total_benef
            else:
                time_benef[oblast] = {date: total_benef}
            if time_benef_category.get(category):
                if time_benef_category[category].get(date):
                    time_benef_category[category][date] += total_benef
                else:
                    time_benef_category[category][date] = total_benef
            else:
                time_benef_category[category] = {date: total_benef}

            family_oblast[oblast] = (
                family_oblast_buffer[oblast]["benef"]
                / family_oblast_buffer[oblast]["qty"]
            )
            family_category[category] = (
                family_category_buffer[category]["benef"]
                / family_category_buffer[category]["qty"]
            )
            pwd_oblast[oblast] = (
                (pwd_oblast_buffer[oblast] * 100)
                / family_oblast_buffer[oblast]["benef"]
                if family_oblast_buffer[oblast]["benef"] != 0
                else 0
            )
            pwd_category[category] = (
                (pwd_category_buffer[category] * 100)
                / family_category_buffer[category]["benef"]
                if family_category_buffer[category]["benef"] != 0
                else 0
            )
            children_oblast[oblast] = (
                children_oblast_buffer[oblast]["benef"]
                / children_oblast_buffer[oblast]["qty"]
            )
            children_category[category] = (
                children_category_buffer[category]["benef"]
                / children_category_buffer[category]["qty"]
            )

            global_gender["male"] += demography["male_benef"]
            global_gender["female"] += demography["female_benef"]

        result = {
            "global_demography_category": json.dumps(global_demography_category),
            "global_demography_category_oblasts": json.dumps(
                global_demography_category_oblasts
            ),
            "global_age_category": json.dumps(global_age_category),
            "global_gender": json.dumps(global_gender),
            "family_oblast": json.dumps(family_oblast),
            "family_category": json.dumps(family_category),
            "pwd_oblast": json.dumps(pwd_oblast),
            "pwd_category": json.dumps(pwd_category),
            "children_oblast": json.dumps(children_oblast),
            "time_benef": json.dumps(time_benef),
            "time_benef_category": json.dumps(time_benef_category),
            "children_category": json.dumps(children_category),
        }

        return result
