from datetime import date, datetime

import pytest
from core import settings
from datasets.models import CityCouncilBid, CityCouncilContract
from datasets.webservices.citycouncil import (
    add_bid,
    add_contract,
    remove_bid,
    remove_contract,
    update_bid,
    update_contract,
)
from model_bakery import baker


@pytest.mark.django_db
class TestBid:
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
        updated_bid = update_bid(record)
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


@pytest.mark.django_db
class TestContract:
    def test_add_contract(self):
        assert CityCouncilContract.objects.count() == 0
        record = {
            "codCon": "43",
            "dsCon": "CONTRATO Nº 004/2014 - PRESTAÇÃO DE SERVIÇO",
            "objetoCon": "Contratação conforme Licitação 01/2014, Pregão 01/2014.",
            "cpfCnpjCon": "92.559.830/0001-71",
            "nmCon": "GREEN CARD S/A REFEIÇÕES COMÉRCIO E SERVIÇOS",
            "valorCon": "1157115,96",
            "dtCon": "28/3/2014",
            "dtConfim": "27/3/2015",
            "excluido": "N",
        }
        contract_obj = add_contract(record)

        expected_expense = {
            "external_code": "43",
            "description": "CONTRATO Nº 004/2014 - PRESTAÇÃO DE SERVIÇO",
            "details": "Contratação conforme Licitação 01/2014, Pregão 01/2014.",
            "company_or_person_document": "92.559.830/0001-71",
            "company_or_person": "GREEN CARD S/A REFEIÇÕES COMÉRCIO E SERVIÇOS",
            "value": 1157115.96,
            "start_date": date(2014, 3, 28),
            "end_date": date(2015, 3, 27),
            "excluded": False,
        }

        assert CityCouncilContract.objects.count() == 1
        assert contract_obj.external_code == expected_expense["external_code"]
        assert contract_obj.description == expected_expense["description"]
        assert contract_obj.details == expected_expense["details"]
        assert (
            contract_obj.company_or_person_document
            == expected_expense["company_or_person_document"]
        )
        assert contract_obj.company_or_person == expected_expense["company_or_person"]
        assert contract_obj.value == expected_expense["value"]
        assert contract_obj.start_date == expected_expense["start_date"]
        assert contract_obj.end_date == expected_expense["end_date"]
        assert contract_obj.excluded == expected_expense["excluded"]

    def test_update_contract(self):
        contract = baker.make_recipe(
            "datasets.models.CityCouncilContract", external_code="43"
        )
        record = {
            "codCon": "43",
            "dsCon": "CONTRATO Nº 004/2014 - PRESTAÇÃO DE SERVIÇO",
            "objetoCon": "Contratação conforme Licitação 01/2014, Pregão 01/2014.",
            "cpfCnpjCon": "92.559.830/0001-71",
            "nmCon": "GREEN CARD S/A REFEIÇÕES COMÉRCIO E SERVIÇOS",
            "valorCon": "1157115,96",
            "dtCon": "28/3/2014",
            "dtConfim": "27/3/2015",
            "excluido": "N",
        }
        updated_contract = update_contract(record)

        assert contract.pk == updated_contract.pk

    def test_remove_contract(self):
        contract = baker.make_recipe(
            "datasets.models.CityCouncilContract", external_code="214", excluded=False
        )
        record = {"codCon": "214"}
        remove_contract(record)

        contract.refresh_from_db()
        assert contract.excluded is True
