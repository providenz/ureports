def create_photo_choices(data_entries):
    settlements = set(
        data_entries.values_list("place__settlement", "place__settlement").distinct()
    )
    settlement_choices = sorted(list(settlements))
    oblasts = set(
        data_entries.exclude(place__oblast__isnull=True)
        .values_list("place__oblast", "place__oblast")
        .distinct()
    )
    oblasts_choices = [("", "All regions")] + sorted(list(oblasts))
    return settlement_choices, oblasts_choices


def create_table_choices(data_entries):
    settlements = set(
        data_entries.values_list("place__settlement", "place__settlement").distinct()
    )
    settlements_choices = list(settlements)
    oblasts = set(data_entries.values_list("place__oblast", "place__oblast").distinct())
    oblasts_choices = [("", "All oblasts")] + list(oblasts)
    return settlements_choices, oblasts_choices
