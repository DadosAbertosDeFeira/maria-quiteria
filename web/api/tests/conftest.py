from datetime import date

import pytest
from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User(username="marvin", password="paranoidandroid")


@pytest.fixture
def api_client_authenticated(api_client, user):
    api_client.force_authenticate(user)
    return api_client


@pytest.fixture
def url():
    return "/api/"


@pytest.fixture
def one_gazette():
    return baker.make_recipe("datasets.Gazette", date=date(2021, 4, 21))


@pytest.fixture
def last_of_two_gazettes():
    baker.make_recipe("datasets.Gazette", date=date(2021, 3, 5))
    return baker.make_recipe("datasets.Gazette", date=date(2021, 4, 21))


@pytest.fixture
def last_of_three_gazettes():
    baker.make_recipe("datasets.Gazette", date=date(2021, 1, 1), power="executivo")
    baker.make_recipe(
        "datasets.GazetteEvent",
        summary="Life? Don't talk to me about life.",
        gazette__date=date(2021, 3, 5),
        gazette__power="legislativo",
    )
    return baker.make_recipe(
        "datasets.Gazette", date=date(2021, 4, 21), power="executivo"
    )
