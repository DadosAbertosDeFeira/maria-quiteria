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

        data = response.json()["results"]
        assert data[0]["date"] == presenca.date.strftime("%Y-%m-%d")
        assert data[0]["description"] == presenca.description
        assert data[0]["council_member"] == presenca.council_member
        assert data[0]["status"] == presenca.status
        assert len(data) == 1

    @pytest.mark.parametrize(
        "data, quantity_expected",
        [
            ({"query": "Competente da Silva"}, 3),
            ({"start_date": "2020-3-18"}, 0),
            ({"end_date": "2020-9-11"}, 3),
            ({"start_date": "2020-9-11", "end_date": "2020-9-15"}, 0),
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

        baker.make_recipe("datasets.CityCouncilAttendanceList", _quantity=3)

        response = api_client_authenticated.get(self.url, data=data)
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()["results"]) == quantity_expected

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


class TestGazetteView:
    url = reverse("gazettes-list")

    def test_should_list_no_gazette(self, api_client_authenticated):
        response = api_client_authenticated.get(self.url)
        assert response.status_code == HTTPStatus.OK

        data = response.json()["results"]
        assert len(data) == 0

    def test_should_list_one_gazette_with_correct_content(
        self, api_client_authenticated, one_gazette
    ):
        response = api_client_authenticated.get(self.url)
        assert response.status_code == HTTPStatus.OK

        data = response.json()["results"]
        assert data[0]["crawled_from"] == one_gazette.crawled_from
        assert data[0]["date"] == one_gazette.date.strftime("%Y-%m-%d")
        assert data[0]["power"] == one_gazette.power
        assert data[0]["year_and_edition"] == one_gazette.year_and_edition
        assert len(data) == 1

    def test_should_list_more_than_one_gazettes(
        self, api_client_authenticated, last_of_two_gazettes
    ):
        response = api_client_authenticated.get(self.url)
        assert response.status_code == HTTPStatus.OK

        data = response.json()["results"]
        assert len(data) == 2

    @pytest.mark.parametrize(
        "data,quantity_expected",
        [
            ({"query": "life"}, 1),
            ({"power": "executivo"}, 2),
            ({"start_date": "2021-01-02"}, 2),
            ({"end_date": "2021-03-15"}, 2),
            ({"start_date": "2021-01-02", "end_date": "2021-03-15"}, 1),
            (
                {
                    "query": "talk",
                    "power": "legislativo",
                    "start_date": "2021-01-01",
                    "end_date": "2021-04-30",
                },
                1,
            ),
            ({}, 3),
        ],
        ids=[
            "filter_by_query",
            "filter_by_power",
            "filter_by_start_date",
            "filter_by_end_date",
            "filter_by_range_date",
            "filter_by_query_power_and_range_date",
            "filter_by_non",
        ],
    )
    def test_should_filter_gazettes(
        self, data, quantity_expected, api_client_authenticated, last_of_three_gazettes
    ):
        response = api_client_authenticated.get(self.url, data=data)
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()["results"]) == quantity_expected


class TestCityCouncilMinuteView:
    url = reverse("city-council-minute")

    def test_should_list_city_council_minute(self, api_client_authenticated):
        minute = baker.make_recipe("datasets.CityCouncilMinute")
        baker.make_recipe("datasets.CityCouncilMinute")

        response = api_client_authenticated.get(self.url)

        assert response.status_code == HTTPStatus.OK

        data = response.json()["results"]
        assert data[0]["date"] == minute.date.strftime("%Y-%m-%d")
        assert data[0]["event_type"] == minute.event_type
        assert data[0]["title"] == minute.title
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
    def test_should_filter_city_council_minute(
        self, api_client_authenticated, data, quantity_expected
    ):
        baker.make_recipe(
            "datasets.CityCouncilMinute", title="test", date=date(2020, 3, 18)
        )
        baker.make_recipe("datasets.CityCouncilMinute", date=date(2020, 3, 20))
        baker.make_recipe("datasets.CityCouncilMinute", date=date(2020, 5, 20))

        response = api_client_authenticated.get(self.url, data=data)

        assert response.status_code == HTTPStatus.OK
        assert len(response.json()["results"]) == quantity_expected

    def test_filter_date_when_is_passing_wrong_format(self, api_client_authenticated):
        baker.make_recipe("datasets.CityCouncilMinute")

        with pytest.raises(exceptions.ValidationError) as exc:
            api_client_authenticated.get(self.url, data={"start_date": "18-03-2020"})
            assert exc.value.message == (
                'O valor "%(value)s" tem um formato de data inválido.'
                "Deve ser no formato  YYY-MM-DD."
            )


class TestCityHallBidView:
    url = reverse("city-hall-bids")

    def test_should_list_city_hall_bids(self, api_client_authenticated):
        baker.make_recipe("datasets.CityHallBid", _quantity=3)

        response = api_client_authenticated.get(self.url)

        data = response.json()["results"]

        assert response.status_code == HTTPStatus.OK
        assert len(data) == 3

    @pytest.mark.parametrize(
        "data,quantity_expected",
        [
            ({"query": "Aquisição de materiais"}, 1),
            ({"start_date": "2020-02-20"}, 3),
            ({"end_date": "2020-03-20"}, 2),
            ({"start_date": "2020-02-17", "end_date": "2020-03-30"}, 3),
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
    def test_should_filter_bids(
        self, api_client_authenticated, data, quantity_expected
    ):
        baker.make_recipe(
            "datasets.CityHallBid",
            description="Aquisição de materiais de limpeza",
            session_at=date(2020, 3, 18),
        )
        baker.make_recipe(
            "datasets.CityHallBid",
            description="material de higienização",
            session_at=date(2020, 3, 20),
        )
        baker.make_recipe(
            "datasets.CityHallBid",
            description="e quantificação de hemoglobinas",
            session_at=date(2020, 3, 24),
        )

        response = api_client_authenticated.get(self.url, data=data)
        data = response.json()["results"]

        assert response.status_code == HTTPStatus.OK
        assert len(data) == quantity_expected

