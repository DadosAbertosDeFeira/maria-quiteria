import json
from datetime import date, datetime, timedelta

import pytest
from django.conf import settings
from model_bakery import baker
from requests import HTTPError
from web.datasets.models import (
    CityCouncilBid,
    CityCouncilContract,
    CityCouncilExpense,
    CityCouncilRevenue,
    SyncInformation,
)
from web.datasets.tasks import (
    WebserviceException,
    add_citycouncil_bid,
    add_citycouncil_contract,
    add_citycouncil_expense,
    add_citycouncil_revenue,
    backup_file,
    content_from_file,
    distribute_city_council_objects_to_sync,
    get_city_council_updates,
    remove_citycouncil_bid,
    remove_citycouncil_contract,
    remove_citycouncil_expense,
    remove_citycouncil_revenue,
    update_citycouncil_bid,
    update_citycouncil_contract,
    update_citycouncil_expense,
    update_citycouncil_revenue,
)


@pytest.fixture
def parser(mocker):
    parser_mock = mocker.patch("web.datasets.tasks.parser")
    parser_mock.from_file.return_value = {"content": "quarenta e dois"}
    return parser_mock


@pytest.fixture
def path(mocker):
    path_mock = mocker.patch("web.datasets.tasks.Path")
    path_mock.return_value.exists.return_value = True
    return path_mock


class TestContentFromFile:
    @pytest.mark.django_db
    def test_content_from_file_saved_to_db(self, parser, path):
        gazette = baker.make("datasets.Gazette")
        a_file = baker.make(
            "datasets.File",
            url="https://url.com",
            content_object=gazette,
            checksum="random",
            s3_url="https://dadosabertosdefeira.com/mq/"
            "Termo_de_Referência_-_HOSP_CAMP.pdf",
            s3_file_path="mq/Termo_de_Referência_-_HOSP_CAMP.pdf",
            content=None,
        )

        result = content_from_file.delay(a_file.pk)

        a_file.refresh_from_db()
        assert parser.from_file.called
        assert a_file.content == "quarenta e dois"
        assert result.get() == "quarenta e dois"

    def test_content_from_files_not_saving_to_db(self, parser, path):
        result = content_from_file.delay(path="/tmp/README.md")

        assert result.get() == "quarenta e dois"
        assert parser.from_file.called

    @pytest.mark.django_db
    def test_save_empty_string_when_nothing_is_parsed(self, mocker, path):
        parser_mock = mocker.patch("web.datasets.tasks.parser")
        parser_mock.from_file.return_value = {
            "content": None
        }  # casos onde o pdf é uma imagem
        gazette = baker.make("datasets.Gazette")
        a_file = baker.make(
            "datasets.File",
            url="https://url.com",
            content_object=gazette,
            checksum="random",
            s3_url="https://dadosabertosdefeira.com/mq/"
            "Termo_de_Referência_-_HOSP_CAMP.pdf",
            s3_file_path="mq/Termo_de_Referência_-_HOSP_CAMP.pdf",
            content=None,
        )

        result = content_from_file.delay(a_file.pk)
        a_file.refresh_from_db()

        assert parser_mock.from_file.called
        assert result.get() == ""
        assert a_file.content == ""


@pytest.mark.django_db
class TestBackupFile:
    def test_backup_file(self):
        url = "https://www.dadosabertosdefeira.com.br/fake_file.pdf"
        gazette = baker.make("datasets.Gazette")
        a_file = baker.make(
            "datasets.File", url=url, content_object=gazette, checksum="random"
        )
        expected_s3_file_path = (
            f"maria-quiteria-local/files/gazette/"
            f"{a_file.created_at.year}/{a_file.created_at.month}/"
            f"{a_file.created_at.day}/random-fake_file.pdf"
        )
        expected_s3_url = (
            f"https://teste.s3.brasil.amazonaws.com/{expected_s3_file_path}"
        )

        backup_file.delay(a_file.pk)

        a_file.refresh_from_db()

        assert a_file.s3_url == expected_s3_url
        assert a_file.s3_file_path == expected_s3_file_path

    def test_return_none_when_file_does_not_exist(self):
        result = backup_file.delay(9)
        assert result.get() is None

    def test_return_none_when_file_has_backup_already(self):
        gazette = baker.make("datasets.Gazette")
        a_file = baker.make(
            "datasets.File",
            url="https://url.com",
            content_object=gazette,
            checksum="random",
            s3_url="https://s3url.com",
        )
        result = backup_file.delay(a_file.pk)
        assert result.get() is None


@pytest.mark.django_db
class TestGetCityCouncilUpdates:
    def test_get_city_council_updates(self, mocker):
        expected_payload = {
            "inclusoesContrato": [],
            "alteracoesContrato": [],
            "exclusoesContrato": [],
            "inclusoesLicitacao": [],
            "alteracoesLicitacao": [
                {
                    "codLic": "214",
                    "codTipoLic": "7",
                    "numLic": "004/2020",
                    "numTipoLic": "004/2020",
                    "objetoLic": "Contratação de pessoa jurídica",
                    "dtLic": "2020-03-26 09:00:00",
                }
            ],
            "exclusoesLicitacao": [],
            "inclusoesReceita": [],
            "alteracoesReceita": [],
            "exclusoesReceita": [],
            "inclusoesDespesa": [],
            "alteracoesDespesa": [],
            "exclusoesDespesa": [],
        }
        post_mock = mocker.patch("web.datasets.tasks.requests.get")
        post_mock.return_value.status_code = 200
        post_mock.return_value.json.return_value = expected_payload
        yesterday = date.today() - timedelta(days=1)
        formatted_yesterday = yesterday.strftime("%Y-%m-%d")

        result = get_city_council_updates.delay(formatted_yesterday)
        assert result.get() == expected_payload

        assert post_mock.called
        assert post_mock.call_args_list[0][1]["params"]["data"] == formatted_yesterday

        sync_info = SyncInformation.objects.get()
        assert sync_info.date == yesterday
        assert sync_info.source == "camara"
        assert sync_info.succeed is True
        assert sync_info.response == expected_payload

    def test_handle_with_error_when_parameters_are_invalid(self, mocker):
        expected_payload = {"erro": "Os parametros enviados são inválidos."}
        post_mock = mocker.patch("web.datasets.tasks.requests.get")
        post_mock.return_value.json.return_value = expected_payload
        tomorrow = date.today() + timedelta(days=1)

        with pytest.raises(WebserviceException):
            result = get_city_council_updates.delay(tomorrow.strftime("%Y-%m-%d"))
            result.get()
            assert result.failed() is True
            assert "Os parametros enviados são inválidos." in result.traceback

        sync_info = SyncInformation.objects.get()
        assert sync_info.date == tomorrow
        assert sync_info.source == "camara"
        assert sync_info.succeed is False
        assert sync_info.response == expected_payload

    def test_raise_exception_if_request_is_not_successful(self, mocker):
        post_mock = mocker.patch("web.datasets.tasks.requests.get")
        post_mock.return_value.raise_for_status.side_effect = HTTPError()
        yesterday = date.today() - timedelta(days=1)

        with pytest.raises(HTTPError):
            result = get_city_council_updates.delay(yesterday.strftime("%Y-%m-%d"))
            result.get()
            assert result.failed() is True

        sync_info = SyncInformation.objects.get()
        assert sync_info.date == yesterday
        assert sync_info.source == "camara"
        assert sync_info.succeed is False
        assert sync_info.response is None


class TestDistributeCityCouncilObjectsToSync:
    def test_distribute_city_council_objects_to_sync(self, mocker):
        record_data = {
            "codLic": "214",
            "objetoLic": "Contratação de pessoa jurídica",
            "dtLic": "2020-04-26 09:00:00",
        }
        payload = {
            "inclusoesContrato": [],
            "alteracoesContrato": [],
            "exclusoesContrato": [],
            "inclusoesLicitacao": [],
            "alteracoesLicitacao": [record_data],
            "exclusoesLicitacao": [],
            "inclusoesReceita": [],
            "alteracoesReceita": [],
            "exclusoesReceita": [],
            "inclusoesDespesa": [],
            "alteracoesDespesa": [],
            "exclusoesDespesa": [],
        }
        task = mocker.patch("web.datasets.tasks.update_citycouncil_bid.delay")
        task.return_value.queue_name = "default"

        distribute_city_council_objects_to_sync.delay(payload)

        assert task.called is True
        assert task.call_count == 1
        assert task.call_args_list[0][0][0] == record_data

    def test_do_not_call_task_if_there_is_no_records(self, mocker):
        payload = {
            "inclusoesContrato": [],
            "alteracoesContrato": [],
            "exclusoesContrato": [],
            "inclusoesLicitacao": [],
            "alteracoesLicitacao": [],
            "exclusoesLicitacao": [],
            "inclusoesReceita": [],
            "alteracoesReceita": [],
            "exclusoesReceita": [],
            "inclusoesDespesa": [],
            "alteracoesDespesa": [],
            "exclusoesDespesa": [],
        }

        task = mocker.patch("web.datasets.tasks.update_citycouncil_bid.delay")
        task.return_value.queue_name = "default"

        distribute_city_council_objects_to_sync.delay(payload)

        assert task.called is False

    @pytest.mark.parametrize(
        "payload_filename",
        [
            "web/datasets/tests/fixtures/response-20042021.json",
            "web/datasets/tests/fixtures/response-22042021.json",
            "web/datasets/tests/fixtures/response-23042021.json",
        ],
    )
    def test_distribution_with_real_payloads(self, payload_filename):
        payload = json.loads(open(payload_filename).read())
        distribute_city_council_objects_to_sync.delay(payload)


@pytest.mark.django_db
class TestCityCouncilBid:
    def test_add_citycouncil_bid(self):
        assert CityCouncilBid.objects.count() == 0

        record = {
            "codLic": "214",
            "codTipoLic": "7",
            "numLic": "004/2020",
            "numTipoLic": "004/2020",
            "objetoLic": "Contratação de pessoa jurídica",
            "dtLic": "2020-03-26 09:00:00",
            "arquivos": [],
        }
        result = add_citycouncil_bid.delay(record)
        bid = result.get()
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
        assert bid.files.count() == 0

    def test_do_not_duplicate_existent_citycouncil_bid(self):
        assert CityCouncilBid.objects.count() == 0

        record = {
            "codLic": "214",
            "codTipoLic": "7",
            "numLic": "004/2020",
            "numTipoLic": "004/2020",
            "objetoLic": "Contratação de pessoa jurídica",
            "dtLic": "2020-03-26 09:00:00",
            "arquivos": [],
        }
        add_citycouncil_bid.delay(record)
        add_citycouncil_bid.delay(record)
        add_citycouncil_bid.delay(record)

        assert CityCouncilBid.objects.count() == 1

    def test_add_citycouncil_bid_with_files(self, mock_backup_file):
        assert CityCouncilBid.objects.count() == 0

        record = {
            "codLic": "214",
            "codTipoLic": "7",
            "numLic": "004/2020",
            "numTipoLic": "004/2020",
            "objetoLic": "Contratação de pessoa jurídica",
            "dtLic": "2020-03-26 09:00:00",
            "arquivos": [
                {
                    "codArqLic": "1396",
                    "codLic": "214",
                    "dsArqLic": "publicacao.doc",
                    "caminhoArqLic": "upload/licitacao/publicacao.doc",
                },
                {
                    "codArqLic": "1397",
                    "codLic": "214",
                    "dsArqLic": "publicacao2.doc",
                    "caminhoArqLic": "upload/licitacao/publicacao2.doc",
                },
            ],
        }
        result = add_citycouncil_bid.delay(record)
        bid = result.get()
        assert CityCouncilBid.objects.count() == 1
        assert bid.files.count() == 2

    def test_update_citycouncil_bid(self):
        bid = baker.make_recipe("datasets.CityCouncilBid", external_code=214)
        record = {
            "codLic": "214",
            "codTipoLic": "7",
            "numLic": "004/2020",
            "numTipoLic": "004/2020",
            "objetoLic": "Contratação de pessoa jurídica",
            "dtLic": "2020-03-26 09:00:00",
            "arquivos": [],
        }
        result = update_citycouncil_bid.delay(record)
        updated_bid = result.get()
        assert bid.pk == updated_bid.pk
        assert updated_bid.modality == "pregao_presencial"
        assert updated_bid.code == record["numLic"]
        assert updated_bid.code_type == record["numTipoLic"]
        assert updated_bid.description == record["objetoLic"]
        assert updated_bid.session_at == datetime(2020, 3, 26, 9, 0, 0)
        assert updated_bid.excluded is False

    def test_remove_citycouncil_bid(self):
        bids = baker.make_recipe("datasets.CityCouncilBid", excluded=False, _quantity=3)
        record = [{"codLic": bid.external_code} for bid in bids]
        remove_citycouncil_bid.delay(record)

        for bid in bids:
            bid.refresh_from_db()
            assert bid.excluded is True

    def test_update_citycouncil_files(self, mock_backup_file):
        bid = baker.make_recipe("datasets.CityCouncilBid", external_code=214)
        assert bid.files.count() == 0

        record = {
            "codLic": "214",
            "arquivos": [
                {
                    "codArqLic": "1396",
                    "codLic": "215",
                    "dsArqLic": "publicacao.doc",
                    "caminhoArqLic": "upload/licitacao/publicacao.doc",
                }
            ],
        }
        result = update_citycouncil_bid.delay(record)
        updated_bid = result.get()
        assert bid.pk == updated_bid.pk
        assert bid.files.count() == 1


@pytest.mark.django_db
class TestCityCouncilContract:
    def test_add_citycouncil_contract(self):
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
            "arquivos": [],
        }
        result = add_citycouncil_contract.delay(record)
        contract_obj = result.get()

        expected_contract = {
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
        assert contract_obj.external_code == expected_contract["external_code"]
        assert contract_obj.description == expected_contract["description"]
        assert contract_obj.details == expected_contract["details"]
        assert (
            contract_obj.company_or_person_document
            == expected_contract["company_or_person_document"]
        )
        assert contract_obj.company_or_person == expected_contract["company_or_person"]
        assert contract_obj.value == expected_contract["value"]
        assert contract_obj.start_date == expected_contract["start_date"]
        assert contract_obj.end_date == expected_contract["end_date"]
        assert contract_obj.excluded == expected_contract["excluded"]

    def test_do_not_duplicate_existent_citycouncil_contract(self):
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
            "arquivos": [],
        }
        add_citycouncil_contract.delay(record)
        add_citycouncil_contract.delay(record)
        add_citycouncil_contract.delay(record)

        assert CityCouncilContract.objects.count() == 1

    def test_add_citycouncil_contract_with_files(self, mock_backup_file):
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
            "arquivos": [
                {
                    "codArqCon": "1396",
                    "codCon": "43",
                    "dsArqCon": "publicacao.doc",
                    "caminho": "upload/publicacao.doc",
                }
            ],
        }
        result = add_citycouncil_contract.delay(record)
        contract_obj = result.get()

        assert CityCouncilContract.objects.count() == 1
        assert contract_obj.files.count() == 1

    def test_update_citycouncil_contract(self):
        contract = baker.make_recipe("datasets.CityCouncilContract", external_code=43)
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
            "arquivos": [],
        }
        result = update_citycouncil_contract.delay(record)
        updated_contract = result.get()

        assert contract.pk == updated_contract.pk

    def test_update_citycouncil_contract_with_files(self, mock_backup_file):
        contract = baker.make_recipe("datasets.CityCouncilContract", external_code=43)
        assert contract.files.count() == 0
        record = {
            "codCon": "43",
            "arquivos": [
                {
                    "codArqCon": "1396",
                    "codCon": "43",
                    "dsArqCon": "publicacao.doc",
                    "caminho": "upload/publicacao.doc",
                }
            ],
        }
        result = update_citycouncil_contract.delay(record)
        updated_contract = result.get()

        assert contract.pk == updated_contract.pk
        assert updated_contract.files.count() == 1

    def test_remove_citycouncil_contracts(self):
        contracts = baker.make_recipe(
            "datasets.CityCouncilContract", excluded=False, _quantity=3
        )
        records = [{"codCon": contract.external_code} for contract in contracts]
        remove_citycouncil_contract.delay(records)

        for contract in contracts:
            contract.refresh_from_db()
            assert contract.excluded is True


@pytest.mark.django_db
class TestCityCouncilRevenue:
    def test_add_citycouncil_revenue(self):
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
        result = add_citycouncil_revenue.delay(record)
        revenue_obj = result.get()

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

    def test_do_not_duplicate_existent_citycouncil_revenue(self):
        assert CityCouncilRevenue.objects.count() == 0
        record = {
            "codLinha": "240",
            "codUnidGestora": "101",
            "dtPublicacao": "2021-04-19",
            "dtRegistro": "2021-04-19",
            "tipoRec": "TRANSF",
            "modalidade": "TRANSFERENCIA DUODECIMO",
            "dsReceita": "Repasse Efetuado nesta Data",
            "valor": "2568658.68",
            "fonte": "PREFEITURA",
            "dsNatureza": "4.5.1.2.2.02.02.01.000.0000 - Transferencias Recebidas",
            "destinacao": "ORÇAMENTO",
        }
        add_citycouncil_revenue.delay(record)
        add_citycouncil_revenue.delay(record)
        add_citycouncil_revenue.delay(record)

        assert CityCouncilRevenue.objects.count() == 1

    def test_update_citycouncil_revenue(self):
        revenue = baker.make_recipe("datasets.CityCouncilRevenue", external_code=43)
        record = {
            "codLinha": "43",
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
        result = update_citycouncil_revenue.delay(record)
        updated_revenue = result.get()

        assert revenue.pk == updated_revenue.pk

    def test_remove_citycouncil_revenue(self):
        revenues = baker.make_recipe(
            "datasets.CityCouncilRevenue", excluded=False, _quantity=3
        )
        records = [{"codLinha": revenue.external_code} for revenue in revenues]
        remove_citycouncil_revenue.delay(records)

        for revenue in revenues:
            revenue.refresh_from_db()
            assert revenue.excluded is True


@pytest.mark.django_db
class TestCityCouncilExpense:
    def test_add_citycouncil_expense(self):
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
        result = add_citycouncil_expense.delay(record)
        expense_obj = result.get()

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
            "external_file_code": 253,
            "external_file_line": 2,
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

    def test_do_not_duplicate_existent_citycouncil_expense(self):
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
        add_citycouncil_expense.delay(record)
        add_citycouncil_expense.delay(record)
        add_citycouncil_expense.delay(record)

        assert CityCouncilExpense.objects.count() == 1

    def test_update_citycouncil_expense(self):
        expense = baker.make_recipe(
            "datasets.CityCouncilExpense",
            external_file_code=253,
            external_file_line=2,
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
        result = update_citycouncil_expense.delay(record)
        updated_expense = result.get()

        assert expense.pk == updated_expense.pk

    def test_remove_citycouncil_expense(self):
        expenses = baker.make_recipe(
            "datasets.CityCouncilExpense", excluded=False, _quantity=3
        )
        records = [
            {"codigo": expense.external_file_code, "linha": expense.external_file_line}
            for expense in expenses
        ]
        remove_citycouncil_expense.delay(records)

        for expense in expenses:
            expense.refresh_from_db()
            assert expense.excluded is True
