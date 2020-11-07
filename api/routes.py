from api.views import HealthCheckView
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path("datasets/", include(router.urls)),
    path("", HealthCheckView.as_view()),
]
