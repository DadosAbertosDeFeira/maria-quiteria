from api.views import HealthCheckView
from django.urls import path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path("", HealthCheckView.as_view()),
]
