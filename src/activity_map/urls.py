from django.urls import path

from activity_map.views import (
    MarkerListAPIView,
    maps,
    GetMarkerPhotosView,
    RegionsListAPIView,
)

urlpatterns = [
    path("maps/", maps, name="maps"),
    path("api/markers/", MarkerListAPIView.as_view(), name="marker-list-all"),
    path(
        "api/get_marker_photos/<int:marker_id>/",
        GetMarkerPhotosView.as_view(),
        name="photo-markers",
    ),
    path("api/get_regions_data/", RegionsListAPIView.as_view(), name="regions-data"),
]
