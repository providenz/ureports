from django.urls import path
from . import views

urlpatterns = [
    path(
        "project/<slug:project_slug>/photos/",
        views.project_photos,
        name="project_photos",
    ),
    path(
        "project/<slug:project_slug>/category/<slug:category_slug>/photos/",
        views.project_photos,
        name="project_category_photos",
    ),
    path(
        "get_all_settlements/",
        views.get_all_settlements,
        name="get-all-cities",
    ),
    path(
        "get_settlements/<slug:project_slug>/<slug:category_slug>/",
        views.get_settlements,
        name="get-cities",
    ),
    path(
        "project/<slug:project_slug>/photos/",
        views.project_photos,
        name="project_photos",
    ),
    path(
        "project/<slug:project_slug>/category/<slug:category_slug>/photos/",
        views.project_photos,
        name="project_category_photos",
    ),
    path("photos/", views.photos, name="photos"),
]
# fix
