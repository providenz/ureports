import traceback
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from search_distr.models import Region, Settlement, Distribution, Month, Person, File
from search_distr.forms import PersonForm, XLSXUploadForm, RegionForm, SettlementForm, MonthComparison
from search_distr.utils import (
    get_next_and_previous_months,
    get_or_create_current_month,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.custom_django_functions import get_or_create_object


from search_distr.data_loader.data_loader import DataLoader, DataUploader
from reports.models import Category

@login_required
def index(request):
    if request.user.user_type == "MA" or request.user.is_superuser:
        if request.method == "POST":
            form = RegionForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data["name"]
                get_or_create_object(Region, name=name)
        else:
            form = RegionForm()

        if request.user.manager_access.is_full or request.user.is_superuser:
            regions = Region.objects.all()
        else:
            regions = request.user.manager_access.regions.all()
        return render(request, 'search_distr/index.html', {"regions": regions, "form": form})

 
    else:
        return redirect("login")

@login_required
def region_detail(request, slug):
    if request.user.user_type == "MA" or request.user.is_superuser:
        if request.method == "POST":
            form = SettlementForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data["name"]
                community = form.cleaned_data["community"]
                district = form.cleaned_data["district"]
                region = Region.objects.get(slug=slug)
                get_or_create_object(
                    Settlement,
                    name=name,
                    community=community,
                    district=district,
                    region=region,
                )
        else:
            form = SettlementForm()
        settlements = Settlement.objects.filter(region__slug=slug)


        query = request.GET.get("q")
        if query:
            settlements = settlements.filter(Q(name__icontains=query))
        else:
            query = ''
        return render(
            request,
            "search_distr/region_detail.html",
            {"settlements": settlements, "form": form, "q": query, "r_slug": slug},
        )
    else:
        return redirect("login")

@login_required
def category_choose(request, setl_slug):
    if request.user.user_type == "MA" or request.user.is_superuser:
        categories = Category.objects.all()
        return render(request, "search_distr/categories.html", {"setl_slug": setl_slug, "categories": categories})

@login_required
def settlement_detail(request, setl_slug, category_slug, month_id=None):
    if request.user.user_type == "MA" or request.user.is_superuser:
        settlement = get_object_or_404(Settlement, slug=setl_slug)
        category = Category.objects.get(slug=category_slug)
        distributions = Distribution.objects.filter(person__settlement=settlement, category=category)

        if month_id:
            month = Month.objects.get(id=month_id)
        else:
            month = get_or_create_current_month()
        if request.method == "POST":
            form = PersonForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data["name"]
                address = form.cleaned_data["address"]
                age = form.cleaned_data["age"]
                gender = form.cleaned_data["gender"]
                try:
                    person = Person.objects.get(
                        name=name, address=address, age=age, gender=gender
                    )
                except Person.DoesNotExist:
                    person = Person.objects.create(
                        name=name,
                        address=address,
                        age=age,
                        gender=gender,
                        settlement=settlement,
                    )
                    person.save()
                try:
                    distribution = Distribution.objects.get(person=person, month=month)
                except Distribution.DoesNotExist:
                    distribution = Distribution.objects.create(
                        person=person, month=month
                    )
                    distribution.save()
        else:
            form = PersonForm()

        next_month, prev_month = get_next_and_previous_months(month)
        existing_distributions = distributions.filter(month=month)
        persons = Person.objects.filter(settlement=settlement)

        if not existing_distributions.exists():
            new_distributions = [
                Distribution(month=month, person=person, is_received=False, category=category)
                for person in persons
            ]
            Distribution.objects.bulk_create(new_distributions)

        distributions = Distribution.objects.filter(
            person__settlement=settlement, month=month, category=category
        )
        distributions = distributions.order_by("id")
        return render(
            request,
            "search_distr/settlement_detail.html",
            {
                "distributions": distributions,
                "settlement": settlement,
                "form": form,
                "month": month,
                "next_month": next_month,
                "prev_month": prev_month,
                "category_slug": category_slug
            },
        )
    else:
        return redirect("login")

@login_required
def statistics(request):
    difference = None
    if request.user.is_superuser:
        total_persons = len(Person.objects.all())
        if request.method == "POST":
            form = MonthComparison(request.POST)
            if form.is_valid():
                m1 = form.cleaned_data["m1"]
                y1 = form.cleaned_data["y1"]
                m2 = form.cleaned_data["m2"]
                y2 = form.cleaned_data["y2"]
                category_id = form.cleaned_data["category"]
                if m1 and m2 and y1 and y2 and category_id:
                    category = Category.objects.get(pk=category_id)
                    m1 = datetime.strptime(m1, '%B').month
                    m2 = datetime.strptime(m2, '%B').month
                    month1 = get_or_create_object(Month, month=int(m1), year=int(y1))
                    month2 = get_or_create_object(Month, month=int(m2), year=int(y2))
                    qty1 = len(Distribution.objects.filter(is_received=True, month=month1, category=category))
                    qty2 = len(Distribution.objects.filter(is_received=True, month=month2, category=category))
                    difference = qty1 - qty2
                    difference = f'+{difference}' if difference >= 0 else f'{difference}'
                    return render(
                        request, "search_distr/statistics.html", 
                        {
                            "total": total_persons, 
                            "form": form, 
                            "month1": month1,  
                            "month2": month2,  
                            "qty1": qty1,  
                            "qty2": qty2, 
                            "diff": difference,
                            "category": category,
                        })
        else:
            form = MonthComparison()
        return render(request, "search_distr/statistics.html", {"total": total_persons, "form": form})
    else:
        return redirect("login")
    

@login_required
def load_data(request):
    if request.user.is_superuser:
        if request.method == "POST":
            form = XLSXUploadForm(request.POST, request.FILES)
            if form.is_valid():
                xlsx_file = request.FILES["xlsx_file"]
                try:
                    uploader = DataUploader(xlsx_file)
                    counter = uploader.fill_data()
                except Exception as e:
                    traceback_message = traceback.format_exc()
                    last_traceback_line = traceback_message.splitlines()[-1]
                    return render(request, "search_distr/load_data.html", {"error": last_traceback_line, "form": XLSXUploadForm()})
                return render(
                    request, "search_distr/load_data_success.html", {"counter": counter}
                )
        else:
            form = XLSXUploadForm()
        return render(request, "search_distr/load_data.html", {"form": form})


class ChnageReceived(APIView):
    def get(self, request, id):
        if request.user.user_type == "MA" or request.user.is_superuser:
            distribution = get_object_or_404(Distribution, pk=id)
            distribution.is_received = not distribution.is_received
            distribution.save()
            return Response({"all": "ok"})
        else:
            return Response({"Error": "Not authorized!"}, 401)



class CreateDocxFile(APIView):
    def get(self, request, slug, month_id):

        if request.user.user_type == "MA" or request.user.is_superuser:
            settlement = Settlement.objects.get(slug=slug)
            month = Month.objects.get(id=month_id)
            distributions = Distribution.objects.filter(
                month=month, person__settlement=settlement
            )
            loader = DataLoader(
                settlement=settlement, month=month, distributions=distributions
            )
            loader.set_header()
            loader.fill_doc()
            name = f"{settlement.slug}_{month.month_name}_{month.year}"
            tmp_file = loader.get_file(name)
            file = File(name=name, file=tmp_file)
            file.save()
            return Response({"file_url": file.file.url})
        else:
            return Response({"Error": "Not authorized!"}, 401)




class CreateDocxFileOnlyReceived(APIView):
    def get(self, request, slug, month_id):

        if request.user.user_type == "MA" or request.user.is_superuser:
            settlement = Settlement.objects.get(slug=slug)
            month = Month.objects.get(id=month_id)
            distributions = Distribution.objects.filter(
                month=month, person__settlement=settlement, is_received=True
            )
            loader = DataLoader(
                settlement=settlement, month=month, distributions=distributions
            )
            loader.set_header()
            loader.fill_doc()
            name = f"{settlement.slug}_{month.month_name}_{month.year}"
            tmp_file = loader.get_file(name)
            file = File(name=name, file=tmp_file)
            file.save()
            return Response({"file_url": file.file.url})
        else:
            return Response({"Error": "Not authorized!"}, 401)

