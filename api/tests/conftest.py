import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User(username="marvin", password="paranoidandroid")


@pytest.fixture
def url():
    return "/api/"
