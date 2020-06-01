from datetime import datetime

import pytest
from core import settings
from datasets.models import CityCouncilBid
from datasets.models.bid import add_bid, bid_update, remove_bid
from model_bakery import baker


@pytest.mark.django_db
class TestAddBid:
    def test_add_bid(self):
        assert CityCouncilBid.objects.count() == 0

        record = {
            "codLic": "214",
            "codTipoLic": "7",
            "numLic": "004/2020",
            "numTipoLic": "004/2020",
            "objetoLic": "Contratação de pessoa jurídica",
            "dtLic": "2020-03-26 09:00:00",
        }
        bid = add_bid(record)
        assert CityCouncilBid.objects.count() == 1
        assert isinstance(bid.crawled_at, datetime)
        assert bid.crawled_from == settings.CITY_COUNCIL_WEBSERVICE_ENDPOINT
        assert bid.external_code == record["codLic"]
        assert bid.modality == "pregao_presencial"
        assert bid.code == record["numLic"]
        assert bid.code_type == record["numTipoLic"]
        assert bid.description == record["objetoLic"]
        assert bid.session_at == datetime(2020, 3, 26, 9, 0, 0)
        assert bid.excluded is False

    def test_bid_update(self):
        bid = baker.make_recipe("datasets.models.CityCouncilBid", external_code="214")
        record = {
            "codLic": "214",
            "codTipoLic": "7",
            "numLic": "004/2020",
            "numTipoLic": "004/2020",
            "objetoLic": "Contratação de pessoa jurídica",
            "dtLic": "2020-03-26 09:00:00",
        }
        updated_bid = bid_update(record)
        assert bid.pk == updated_bid.pk
        assert updated_bid.modality == "pregao_presencial"
        assert updated_bid.code == record["numLic"]
        assert updated_bid.code_type == record["numTipoLic"]
        assert updated_bid.description == record["objetoLic"]
        assert updated_bid.session_at == datetime(2020, 3, 26, 9, 0, 0)
        assert updated_bid.excluded is False

    def test_remove_bid(self):
        bid = baker.make_recipe(
            "datasets.models.CityCouncilBid", external_code="214", excluded=False
        )
        record = {"codLic": "214"}
        remove_bid(record)

        bid.refresh_from_db()
        assert bid.excluded is True
