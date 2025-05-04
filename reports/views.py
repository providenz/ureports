import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from reports.models import Project, Category, Dashboard, UpdateDashboard
from data_tables.models import DataTable, RegionStatistic
from activity_map.models import Place
from utils.data_chart_normalizers import DataChartNormalizer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from data_tables.models import geojson_oblasts_names
from reports.utils import get_total_dashboard


@login_required
def index(request):
    if request.user.user_type == "MA":
        return redirect("search_distr")
    if request.user.is_superuser:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(donors=request.user)
    return render(request, "reports/index.html", {"projects": projects})


@login_required
def projects(request):
    # Same logic as in the index view
    if request.user.is_superuser:
        all_projects = Project.objects.all()
    else:
        all_projects = Project.objects.filter(donors=request.user)
    return render(request, "reports/projects.html", {"projects": all_projects})


@login_required
def project_detail(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)

    # Ensure that the user should see this project
    if (
        not request.user.is_superuser
        and not project.donors.filter(id=request.user.id).exists()
    ):
        # You might create a custom 403.html template
        return render(request, "403.html", status=403)

    return render(request, "reports/project_detail.html", {"project": project})


@login_required
def project_category_detail(request, project_slug, category_slug):
    project = get_object_or_404(Project, slug=project_slug)
    category = get_object_or_404(Category, slug=category_slug)

    if category not in project.categories.all():
        # You might create a custom 404.html template
        return render(request, "404.html", status=404)

    context = {
        "project": project,
        "category": category,
    }

    return render(request, "reports/project_category_detail.html", context)


@login_required
def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    return render(request, "reports/category_detail.html", {"category": category})


@login_required
def charts(request):
    if request.user.is_superuser:
        dashboards = Dashboard.objects.all()
    else:
        dashboards = Dashboard.objects.filter(project__donors=request.user)
    total_dashboard = get_total_dashboard(dashboards)
    context = {"dashboard": total_dashboard}

    return render(request, "reports/charts.html", context)


@login_required
def project_category_charts(request, project_slug, category_slug):
    project = get_object_or_404(Project, slug=project_slug)
    category = get_object_or_404(Category, slug=category_slug)

    # get dashboard and last 5 dashboard updates
    dashboard = Dashboard.objects.get(project=project, category=category)
    updates = UpdateDashboard.objects.filter(dashboard=dashboard).order_by("-id")[:5]

    # get last dashboard update
    last_update = updates[0]

    # resorting updates
    updates = sorted(updates, key=lambda x: x.id)

    # check on minimal needed qty of updates for normal visualisation
    while len(updates) < 5:
        updates.append(last_update)

    total_place = len(Place.objects.all())
    region_data = dashboard.region_stats
    region_stats = []
    received_items = dashboard.received_items_stats

    for region in region_data:
        obj = {
            "name": str(region["name"]),
            "oblast": region["oblast"],
            "coverage": round((int(region["settlements"]) / total_place) * 100, 2),
            "places": region["settlements"],
        }
        region_stats.append(obj)

    context = {
        "project": project,
        "category": category,
        "dashboard": dashboard,
        "upds": updates,
        "last_upd": last_update,
        "region_stats": region_stats,
        "received_items": received_items,
    }

    return render(request, "reports/project_category_charts.html", context)


class RegionsDataCharts(APIView):
    def get(self, request, project_slug, category_slug):
        if request.user.is_authenticated:
            project = get_object_or_404(Project, slug=project_slug)
            category = get_object_or_404(Category, slug=category_slug)
            dashboard = Dashboard.objects.get(project=project, category=category)
            total_place = len(Place.objects.all())
            region_data = dashboard.region_stats
            region_stats = []
            for region in region_data:
                obj = {
                    "name": region["name"],
                    "oblast": region["oblast"],
                    "coverage": round(
                        (int(region["settlements"]) / total_place) * 100, 2
                    ),
                    "places": region["settlements"],
                }
                region_stats.append(obj)
            return Response(region_stats, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "Not Authorized"}, status=401)


class RegionDataCharsAll(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                dashboards = Dashboard.objects.all()
            else:
                dashboards = Dashboard.objects.filter(project__donors=request.user)
            total = get_total_dashboard(dashboards)

            region_stats = total["region_stats"]
            return Response(region_stats, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "Not Authorized"}, status=401)
