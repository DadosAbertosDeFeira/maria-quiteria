from django.urls import include, path
from rest_framework import routers

from web.api.views import (
    CityCouncilAgendaView,
    CityCouncilAttendanceListView,
    CityCouncilMinuteView,
    CityHallBidView,
    FrontendEndpoint,
    GazetteView,
    HealthCheckView,
)

router = routers.DefaultRouter()
router.register("", HealthCheckView, basename="root")
router.register("gazettes", GazetteView, basename="gazettes")


urlpatterns = [
    path("", include(router.urls)),
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
    path(
        "city-council/minute/",
        CityCouncilMinuteView.as_view(),
        name="city-council-minute",
    ),
    path("city-hall/bids/", CityHallBidView.as_view(), name="city-hall-bids"),
    path("endpoints", FrontendEndpoint.as_view(), name="frontend-endpoints"),
]
