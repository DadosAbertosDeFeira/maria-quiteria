from api.views import HealthCheckView, CityHallBidView
from django.urls import path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path("", HealthCheckView.as_view()),
    path("city-hall-bid/", CityHallBidView.as_view()),
]
