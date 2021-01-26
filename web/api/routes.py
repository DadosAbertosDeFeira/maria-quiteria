from django.urls import path
from rest_framework import routers

from web.api.views import (
    CityCouncilAgendaView,
    CityCouncilAttendanceListView,
    CityHallBidView,
    HealthCheckView
)

router = routers.DefaultRouter()


urlpatterns = [
    path("", HealthCheckView.as_view()),
    path(
        "city-council/agenda/",
        CityCouncilAgendaView.as_view(),
        name="city-council-agenda",
    ),
    path(
        "city-council/attendance-list/",
        CityCouncilAttendanceListView.as_view(),
        name="city-council-attendance-list",
    ),
    path("city-hall/bids/", CityHallBidView.as_view(), name="city-hall-bids"),
]
