from api.views import CityCouncilAgendaView, CityHallBidView, HealthCheckView
from django.urls import path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path("", HealthCheckView.as_view()),
    path(
        "city-council-agenda/",
        CityCouncilAgendaView.as_view(),
        name="city-council-agenda",
    ),
    path("city-hall-bid/", CityHallBidView.as_view(), name="city-hall-bid"),
]
