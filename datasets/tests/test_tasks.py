from datetime import datetime

import pytest
from datasets.models import CityCouncilBid
from datasets.tasks import (
    WebserviceException,
    backup_file,
    content_from_file,
    get_city_council_updates,
    sync_city_council_objects,
)
from django.utils.timezone import make_aware
from model_bakery import baker


@pytest.fixture
def parser(mocker):
    parser_mock = mocker.patch("datasets.tasks.parser")
    parser_mock.from_file.return_value = {"content": "quarenta e dois"}
    return parser_mock


@pytest.fixture
def path(mocker):
    path_mock = mocker.patch("datasets.tasks.Path")
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

        result = content_from_file(a_file.pk)

        a_file.refresh_from_db()
        assert parser.from_file.called
        assert a_file.content == "quarenta e dois"
        assert result == "quarenta e dois"

    def test_content_from_files_not_saving_to_db(self, parser, path):
        result = content_from_file(path="/tmp/README.md")

        assert result == "quarenta e dois"
        assert parser.from_file.called


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

        backup_file(a_file.pk)

        a_file.refresh_from_db()

        assert a_file.s3_url == expected_s3_url
        assert a_file.s3_file_path == expected_s3_file_path

    def test_return_none_when_file_does_not_exist(self):
        assert backup_file(9) is None

    def test_return_none_when_file_has_backup_already(self):
        gazette = baker.make("datasets.Gazette")
        a_file = baker.make(
            "datasets.File",
            url="https://url.com",
            content_object=gazette,
            checksum="random",
            s3_url="https://s3url.com",
        )
        assert backup_file(a_file.pk) is None


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
        post_mock = mocker.patch("datasets.tasks.requests.post")
        post_mock.return_value.json.return_value = expected_payload

        assert get_city_council_updates() == expected_payload

    def test_handle_with_error_from_the_webservice_when_parameters_are_invalid(
        self, mocker
    ):
        expected_payload = {"erro": "Os parametros enviados são inválidos."}
        post_mock = mocker.patch("datasets.tasks.requests.post")
        post_mock.return_value.json.return_value = expected_payload
        with pytest.raises(WebserviceException) as exception:
            get_city_council_updates()
        assert "Parâmetros inválidos." in str(exception.value)


@pytest.mark.django_db
class TestSyncCityCouncilObjects:
    def test_sync_city_council_objects(self):
        bid = baker.make(
            "datasets.CityCouncilBid",
            external_code="214",
            modality="pregao_presencial",
            code="004/2020",
            code_type="004/2020",
            description="Contratação de pessoa física",
            session_at=datetime(2020, 3, 26, 9, 0, 0),
        )
        payload = {
            "inclusoesContrato": [],
            "alteracoesContrato": [],
            "exclusoesContrato": [],
            "inclusoesLicitacao": [],
            "alteracoesLicitacao": [
                {
                    "codLic": "214",
                    "objetoLic": "Contratação de pessoa jurídica",
                    "dtLic": "2020-04-26 09:00:00",
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
        sync_city_council_objects(payload)

        bid.refresh_from_db()
        assert bid.description == "Contratação de pessoa jurídica"
        assert bid.session_at == make_aware(datetime(2020, 4, 26, 9, 0, 0))

    def test_add_bid_on_update_city_council_objects(self):
        payload = {
            "inclusoesContrato": [],
            "alteracoesContrato": [],
            "exclusoesContrato": [],
            "inclusoesLicitacao": [
                {
                    "codLic": "214",
                    "codTipoLic": "7",
                    "numLic": "004/2020",
                    "numTipoLic": "004/2020",
                    "objetoLic": "Contratação de pessoa jurídica",
                    "dtLic": "2020-03-26 09:00:00",
                }
            ],
            "alteracoesLicitacao": [],
            "exclusoesLicitacao": [],
            "inclusoesReceita": [],
            "alteracoesReceita": [],
            "exclusoesReceita": [],
            "inclusoesDespesa": [],
            "alteracoesDespesa": [],
            "exclusoesDespesa": [],
        }

        assert CityCouncilBid.objects.count() == 0

        sync_city_council_objects(payload)

        assert CityCouncilBid.objects.count() == 1
        bid = CityCouncilBid.objects.first()

        assert bid.external_code == "214"
        assert bid.modality == "pregao_presencial"
        assert bid.code == "004/2020"
        assert bid.code_type == "004/2020"
        assert bid.description == "Contratação de pessoa jurídica"
        assert bid.session_at == make_aware(datetime(2020, 3, 26, 9, 0, 0))
        assert bid.excluded is False

    def test_remove_bid_on_update_city_council_objects(self):
        payload = {
            "inclusoesContrato": [],
            "alteracoesContrato": [],
            "exclusoesContrato": [],
            "inclusoesLicitacao": [],
            "alteracoesLicitacao": [],
            "exclusoesLicitacao": [{"codLic": "214"}],
            "inclusoesReceita": [],
            "alteracoesReceita": [],
            "exclusoesReceita": [],
            "inclusoesDespesa": [],
            "alteracoesDespesa": [],
            "exclusoesDespesa": [],
        }

        bid = baker.make("datasets.CityCouncilBid", external_code="214")
        assert bid.excluded is False

        sync_city_council_objects(payload)
        bid.refresh_from_db()
        assert bid.excluded is True
