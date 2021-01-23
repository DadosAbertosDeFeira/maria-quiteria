from datetime import date
from http import HTTPStatus

import pytest
from django.core import exceptions
from django.urls import reverse
from model_bakery import baker

pytestmark = pytest.mark.django_db


class TestCityCouncilAgendaView:
    url = reverse("city-council-agenda")

    def test_should_list_city_council_agenda(self, api_client_authenticated):
        agenda = baker.make_recipe("datasets.CityCouncilAgenda")
        baker.make_recipe("datasets.CityCouncilAgenda")

        response = api_client_authenticated.get(self.url)

        assert response.status_code == HTTPStatus.OK

        data = response.json()["results"]
        assert data[0]["date"] == agenda.date.strftime("%Y-%m-%d")
        assert data[0]["details"] == agenda.details
        assert data[0]["event_type"] == agenda.event_type
        assert data[0]["title"] == agenda.title
        assert len(data) == 2

    @pytest.mark.parametrize(
        "data,quantity_expected",
        [
            ({"query": "TEST"}, 1),
            ({"start_date": "2020-05-20"}, 1),
            ({"end_date": "2020-03-20"}, 2),
            ({"start_date": "2020-02-20", "end_date": "2020-03-18"}, 1),
            ({}, 3),
        ],
        ids=[
            "filter_by_query",
            "filter_by_start_date",
            "filter_by_end_date",
            "filter_by_range_date",
            "filter_by_non",
        ],
    )
    def test_should_filter_city_council_agenda(
        self, api_client_authenticated, data, quantity_expected
    ):
        baker.make_recipe(
            "datasets.CityCouncilAgenda", details="test", date=date(2020, 3, 18)
        )
        baker.make_recipe("datasets.CityCouncilAgenda", date=date(2020, 3, 20))
        baker.make_recipe("datasets.CityCouncilAgenda", date=date(2020, 5, 20))

        response = api_client_authenticated.get(self.url, data=data)

        assert response.status_code == HTTPStatus.OK
        assert len(response.json()["results"]) == quantity_expected

    def test_filter_date_when_is_passing_wrong_format(self, api_client_authenticated):
        baker.make_recipe("datasets.CityCouncilAgenda")

        with pytest.raises(exceptions.ValidationError) as exc:
            api_client_authenticated.get(self.url, data={"start_date": "18-03-2020"})
            assert exc.value.message == (
                'O valor "%(value)s" tem um formato de data inválido.'
                "Deve ser no formato  YYY-MM-DD."
            )


class TestCityCouncilAttendanceListView:
    url = reverse("city-council-attendance-list")

    def test_should_list_city_council_attendance(self, api_client_authenticated):
        presenca = baker.make_recipe("datasets.CityCouncilAttendanceList")
        response = api_client_authenticated.get(self.url)
        assert response.status_code == HTTPStatus.OK

        data = response.json()
        assert data[0]["date"] == presenca.date.strftime("%Y-%m-%d")
        assert data[0]["description"] == presenca.description
        assert data[0]["council_member"] == presenca.council_member
        assert data[0]["status"] == presenca.status
        assert len(data) == 1

    @pytest.mark.parametrize(
        "data, quantity_expected",
        [
            ({"query": "Competente da Silva"}, 3),
            ({"start_date": "2020-9-15"}, 1),
            ({"end_date": "2020-9-11"}, 1),
            ({"start_date": "2020-9-11", "end_date": "2020-9-15"}, 3),
            ({}, 3),
        ],
        ids=[
            "filter_by_query",
            "filter_by_start_date",
            "filter_by_end_date",
            "filter_by_range_date",
            "filter_by_non",
        ],
    )
    def test_should_filter_city_council_attendance(
        self, api_client_authenticated, data, quantity_expected
    ):

        baker.make_recipe(
            "datasets.CityCouncilAttendanceList",
            date=date(2020, 9, 11),
            description=None,
        )
        baker.make_recipe(
            "datasets.CityCouncilAttendanceList",
            date=date(2020, 9, 13),
            description="description",
        )
        baker.make_recipe(
            "datasets.CityCouncilAttendanceList",
            date=date(2020, 9, 15),
            description="full description",
        )

        response = api_client_authenticated.get(self.url, data=data)
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()) == quantity_expected

    def test_should_throw_exception_when_date_format_wrong(
        self, api_client_authenticated
    ):
        baker.make_recipe("datasets.CityCouncilAttendanceList")

        with pytest.raises(exceptions.ValidationError) as exc:
            api_client_authenticated.get(self.url, data={"start_date": "11-09-2020"})
            assert exc.value.message == (
                'O valor "%(value)s" tem um formato de data inválido.'
                "Deve ser no formato  YYY-MM-DD."
            )
