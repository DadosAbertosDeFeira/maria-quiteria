from datetime import date, datetime

import pytest
from core import settings
from datasets.models import (
    CityCouncilBid,
    CityCouncilContract,
    CityCouncilExpense,
    CityCouncilRevenue,
)
from datasets.webservices.citycouncil import (
    add_bid,
    add_contract,
    add_expense,
    add_revenue,
    remove_bid,
    remove_contract,
    remove_expense,
    update_bid,
    update_contract,
    update_expense,
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


@pytest.mark.django_db
class TestRevenues:
    def test_add_revenue(self):
        assert CityCouncilRevenue.objects.count() == 0
        record = {
            "codLinha": "27",
            "codUnidGestora": "101",
            "dtPublicacao": "1/1/2014",
            "dtRegistro": "1/1/2014",
            "tipoRec": "ORC",
            "modalidade": "RECEBIMENTO",
            "dsReceita": "Repasse Efetuado Nesta Data",
            "valor": "1262150,07",
            "fonte": "PREFEITURA",
            "dsNatureza": "1.7.1.3.01.00.00 - Transferências Correntes",
            "destinacao": "1.7.1.3.01.00.00 - Transferências Correntes",
            "excluido": "N",
        }
        revenue_obj = add_revenue(record)

        expected_revenue = {
            "external_code": "27",
            "budget_unit": "101",
            "published_at": date(2014, 1, 1),
            "registered_at": date(2014, 1, 1),
            "revenue_type": "orcamentaria",
            "modality": "recebimento",
            "description": "Repasse Efetuado Nesta Data",
            "value": 1262150.07,
            "resource": "prefeitura",
            "legal_status": "1.7.1.3.01.00.00 - transferências correntes",
            "destination": "1.7.1.3.01.00.00 - transferências correntes",
            "excluded": False,
        }

        assert CityCouncilRevenue.objects.count() == 1

        assert revenue_obj.external_code == expected_revenue["external_code"]
        assert revenue_obj.budget_unit == expected_revenue["budget_unit"]
        assert revenue_obj.published_at == expected_revenue["published_at"]
        assert revenue_obj.registered_at == expected_revenue["registered_at"]
        assert revenue_obj.revenue_type == expected_revenue["revenue_type"]
        assert revenue_obj.modality == expected_revenue["modality"]
        assert revenue_obj.description == expected_revenue["description"]
        assert revenue_obj.value == expected_revenue["value"]
        assert revenue_obj.resource == expected_revenue["resource"]
        assert revenue_obj.legal_status == expected_revenue["legal_status"]
        assert revenue_obj.destination == expected_revenue["destination"]
        assert revenue_obj.excluded == expected_revenue["excluded"]


@pytest.mark.django_db
class TestExpenses:
    def test_add_expense(self):
        assert CityCouncilExpense.objects.count() == 0
        record = {
            "codArquivo": "253",
            "codEtapa": "EMP",
            "codLinha": "2",
            "codUnidOrcam": "101",
            "dsDespesa": "IMPORTE DESTINADO A PAGAMENTO DE SUBSIDIOS DURANTE O "
            "PERIODO.                                         ",
            "dsFonteRec": "0000 - " "TESOURO",
            "dsFuncao": "01 - " "LEGISLATIVA",
            "dsNatureza": "319011010000000000 - V.Vant.Fixas P.Civil(Ve.Base "
            "Folha)                2003 - Administracao da acao "
            "legislativa                          ",
            "dsSubfuncao": "031 - " "ACAO",
            "dtPublicacao": "2/1/2014",
            "dtRegistro": "2/1/2014",
            "excluido": "N",
            "modalidade": "ISENTO        ",
            "nmCredor": "VEREADORES      ",
            "nuCpfCnpj": "14.488.415/0001-60",
            "numEtapa": "14000001        ",
            "numProcadm": "001/2014      ",
            "numProclic": "              ",
            "valor": "3790000,00",
        }
        expense_obj = add_expense(record)

        expected_expense = {
            "phase": "empenho",
            "budget_unit": "101",
            "summary": "IMPORTE DESTINADO A PAGAMENTO DE SUBSIDIOS DURANTE O PERIODO.",
            "resource": "0000 - TESOURO",
            "function": "01 - LEGISLATIVA",
            "legal_status": "319011010000000000 - V.Vant.Fixas P.Civil(Ve.Base "
            "Folha)                2003 - Administracao da acao "
            "legislativa",
            "subfunction": "031 - ACAO",
            "published_at": date(2014, 1, 2),
            "date": date(2014, 1, 2),
            "excluded": False,
            "modality": "isento",
            "company_or_person": "VEREADORES",
            "document": "14.488.415/0001-60",
            "phase_code": "14000001",
            "number": "001/2014",
            "process_number": "",
            "value": 3790000.00,
            "external_file_code": "253",
            "external_file_line": "2",
        }

        assert CityCouncilExpense.objects.count() == 1

        assert expense_obj.phase == expected_expense["phase"]
        assert expense_obj.budget_unit == expected_expense["budget_unit"]
        assert expense_obj.resource == expected_expense["resource"]
        assert expense_obj.function == expected_expense["function"]
        assert expense_obj.legal_status == expected_expense["legal_status"]
        assert expense_obj.subfunction == expected_expense["subfunction"]
        assert expense_obj.published_at == expected_expense["published_at"]
        assert expense_obj.excluded == expected_expense["excluded"]
        assert expense_obj.modality == expected_expense["modality"]
        assert expense_obj.company_or_person == expected_expense["company_or_person"]
        assert expense_obj.document == expected_expense["document"]
        assert expense_obj.phase_code == expected_expense["phase_code"]
        assert expense_obj.number == expected_expense["number"]
        assert expense_obj.process_number == expected_expense["process_number"]
        assert expense_obj.value == expected_expense["value"]

    def test_update_expense(self):
        expense = baker.make_recipe(
            "datasets.models.CityCouncilExpense",
            external_file_code="253",
            external_file_line="2",
        )
        record = {
            "codArquivo": "253",
            "codEtapa": "EMP",
            "codLinha": "2",
            "codUnidOrcam": "101",
            "dsDespesa": "IMPORTE DESTINADO A PAGAMENTO DE SUBSIDIOS DURANTE O "
            "PERIODO.                                         ",
            "dsFonteRec": "0000 - " "TESOURO",
            "dsFuncao": "01 - " "LEGISLATIVA",
            "dsNatureza": "319011010000000000 - V.Vant.Fixas P.Civil(Ve.Base "
            "Folha)                2003 - Administracao da acao "
            "legislativa                          ",
            "dsSubfuncao": "031 - " "ACAO",
            "dtPublicacao": "2/1/2014",
            "dtRegistro": "2/1/2014",
            "excluido": "N",
            "modalidade": "ISENTO        ",
            "nmCredor": "VEREADORES      ",
            "nuCpfCnpj": "14.488.415/0001-60",
            "numEtapa": "14000001        ",
            "numProcadm": "001/2014      ",
            "numProclic": "              ",
            "valor": "3790000,00",
        }
        updated_expense = update_expense(record)

        assert expense.pk == updated_expense.pk

    def test_remove_expense(self):
        expense = baker.make_recipe(
            "datasets.models.CityCouncilExpense",
            external_file_code="253",
            external_file_line="2",
            excluded=False,
        )
        record = {"codArquivo": "253", "codLinha": "2"}
        remove_expense(record)

        expense.refresh_from_db()
        assert expense.excluded is True
