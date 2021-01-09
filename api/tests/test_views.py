from datetime import date
from http import HTTPStatus

import pytest
from django.core import exceptions
from django.urls import reverse
from model_bakery import baker
from datetime import datetime

pytestmark = pytest.mark.django_db


class TestCityCouncilAgendaView:
    url = reverse("city-council-agenda")

    def test_should_list_city_council_agenda(self, api_client_authenticated):
        agenda = baker.make_recipe("datasets.CityCouncilAgenda")
        baker.make_recipe("datasets.CityCouncilAgenda")

        response = api_client_authenticated.get(self.url)

        assert response.status_code == HTTPStatus.OK

        data = response.json()
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
        assert len(response.json()) == quantity_expected

    def test_filter_date_when_is_passing_wrong_format(self, api_client_authenticated):
        baker.make_recipe("datasets.CityCouncilAgenda")

        with pytest.raises(exceptions.ValidationError) as exc:
            api_client_authenticated.get(self.url, data={"start_date": "18-03-2020"})
            assert exc.value.message == (
                'O valor "%(value)s" tem um formato de data inválido.'
                "Deve ser no formato  YYY-MM-DD."
            )


class TestCityHallBidView:
    url = reverse("city-hall-bid")

    def test_shold_list_city_hall_bids(self, api_client_authenticated):
        session_at = datetime.strptime('2021-01-09 20:17:45-03:00', '%Y-%m-%d %H:%M:%S%z')
        bid = baker.make_recipe("datasets.CityHallBid", session_at=session_at)

        response = api_client_authenticated.get(self.url)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert data[0]["id"] == bid.id

        # o replace e apenas para remover a diferenca entre o formato retornado e o formado do datetime
        # data[0]["session_at"] = '2021-01-09T20:17:45-03:00'
        # str(bid.session_at) = '2021-01-09 20:17:45-03:00'
        assert data[0]["session_at"].replace('T', ' ') == str(bid.session_at)
        assert data[0]["notes"] == bid.notes
        assert data[0]["crawled_from"] == bid.crawled_from
        assert data[0]["public_agency"] == bid.public_agency
        assert data[0]["description"] == bid.description
        assert data[0]["modality"] == bid.modality
        assert data[0]["codes"] == bid.codes

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
    def test_should_filter_bids(
            self, api_client_authenticated, data, quantity_expected
    ):
        baker.make_recipe("datasets.CityHallBid", description="test", session_at=date(2020, 3, 18))
        baker.make_recipe("datasets.CityHallBid", session_at=date(2020, 3, 20))
        baker.make_recipe("datasets.CityHallBid", session_at=date(2020, 5, 20))

        response = api_client_authenticated.get(self.url, data=data)
        assert response.status_code == HTTPStatus.OK
