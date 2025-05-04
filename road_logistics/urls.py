from django.urls import path
from road_logistics import views

urlpatterns = [
    path('rides/', views.rides, name='rides'),
    path('ride-detail/<int:id>/', views.ride_detail, name="ride-detail"),
    path("api/fetch_kobo/", views.FetchKoboAPI.as_view(), name="fetch_kobo_data"),

]
