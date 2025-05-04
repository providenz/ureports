from datetime import datetime
from search_distr.models import Month
from utils.custom_django_functions import  get_or_create_object

def get_date(month, year):
    date_string = f"{year}-{month:02d}-01"
    date_object = datetime.strptime(date_string, "%Y-%m-%d")

    return date_object


def get_last_month(distributions):
    latest_month = Month.objects.order_by("-year", "-month").first()
    return latest_month


def find_next_previous_dates(date_obj, date_list):
    if not date_list:
        return None, None
    date_list.sort()
    index = next((i for i, dt in enumerate(date_list) if dt >= date_obj), None)
    if index is not None:
        previous_date = date_list[index - 1] if index > 0 else None
        next_date = date_list[index + 1] if index < len(date_list) - 1 else None
        return previous_date, next_date
    else:
        return date_list[-1], None


def get_next_and_previous_months(current_month):
    current_date = datetime.now()
    if (
        current_month.year == current_date.year
        and current_month.month == current_date.month
    ):
        next_month_instance = None
    else:
        next_month_year, next_month = current_month.year, current_month.month + 1
        if next_month > 12:
            next_month = 1
            next_month_year += 1
        next_month_instance = get_or_create_object(
            Month,
            year=next_month_year,
            month=next_month,
        )

    prev_month_year, prev_month = current_month.year, current_month.month - 1
    if prev_month < 1:
        prev_month = 12
        prev_month_year -= 1

    prev_month_instance = get_or_create_object(
        Month,
        year=prev_month_year,
        month=prev_month,
    )
    return next_month_instance, prev_month_instance


def get_or_create_current_month():
    current_date = datetime.now()

    current_year = current_date.year
    current_month = current_date.month
    month_instance = get_or_create_object(Month, month=current_month, year=current_year)

    return month_instance
