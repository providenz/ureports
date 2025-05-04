from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("reports.urls")),
    path("", include("accounts.urls")),
    path("", include("photos.urls")),
    path("", include("data_tables.urls")),
    path("", include("activity_map.urls")),
    path("", include("share.urls")),
    path("search_distr/", include('search_distr.urls')),
    path("road_logistics/", include('road_logistics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
