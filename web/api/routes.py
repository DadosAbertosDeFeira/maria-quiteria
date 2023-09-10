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
router.register("datasets/gazettes", GazetteView, basename="gazettes")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "datasets/city-council/agenda/",
        CityCouncilAgendaView.as_view(),
        name="city-council-agenda",
    ),
    path(
        "datasets/city-council/attendance-list/",
        CityCouncilAttendanceListView.as_view(),
        name="city-council-attendance-list",
    ),
    path(
        "datasets/city-council/minute/",
        CityCouncilMinuteView.as_view(),
        name="city-council-minute",
    ),
    path("datasets/city-hall/bids/", CityHallBidView.as_view(), name="city-hall-bids"),
    path("datasets/endpoints", FrontendEndpoint.as_view(), name="frontend-endpoints"),
]
