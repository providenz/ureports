from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("projects/", views.projects, name="projects"),
    path("projects/<slug:project_slug>/", views.project_detail, name="project_detail"),
    path(
        "project/<slug:project_slug>/category/<slug:category_slug>/",
        views.project_category_detail,
        name="project_category_detail",
    ),
    path(
        "category/<slug:category_slug>/", views.category_detail, name="category_detail"
    ),
    path("charts/", views.charts, name="charts"),
    path(
        "project/<slug:project_slug>/category/<slug:category_slug>/charts/",
        views.project_category_charts,
        name="project_category_charts",
    ),
    path(
        "project/<slug:project_slug>/category/<slug:category_slug>/charts_regions/",
        views.RegionsDataCharts.as_view(),
        name="project_category_regions_charts_data",
    ),
    path(
        "charts_regions/",
        views.RegionDataCharsAll.as_view(),
        name="regions_charts_data",
    ),
]
