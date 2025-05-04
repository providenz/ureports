from django.urls import path
from search_distr import views


urlpatterns = [
    path("", views.index, name="search_distr"),
    path("region/<str:slug>/", views.region_detail, name="region_detail"),
    path("settlement/<str:setl_slug>/", views.category_choose, name="category_choose"),
    path("settlement/<str:setl_slug>/<str:category_slug>/", views.settlement_detail, name="settlement_detail"),
    path(
        "settlement/<str:setl_slug>/<str:category_slug>/<int:month_id>/",
        views.settlement_detail,
        name="settlement_detail_month",
    ),
    path(
        "api/change_received/<int:id>/",
        views.ChnageReceived.as_view(),
        name="change_received",
    ),
    path("load_data/", views.load_data, name="load_data"),
    path("statistics/", views.statistics, name="statistics"),
    path(
        "api/load_file/<str:slug>/<int:month_id>/",
        views.CreateDocxFile.as_view(),
        name="create_file",
    ),
    path(
        "api/load_file_received/<str:slug>/<int:month_id>/",
        views.CreateDocxFileOnlyReceived.as_view(),
        name="create_file_only_received",
    ),
]
