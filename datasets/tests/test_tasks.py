import pytest
from datasets.tasks import (
    WebserviceException,
    backup_file,
    content_from_file,
    distribute_city_council_objects_to_sync,
    get_city_council_updates,
)
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
        post_mock.return_value.status_code = 200
        post_mock.return_value.json.return_value = expected_payload

        assert get_city_council_updates() == expected_payload

    def test_handle_with_error_when_parameters_are_invalid(self, mocker):
        expected_payload = {"erro": "Os parametros enviados são inválidos."}
        post_mock = mocker.patch("datasets.tasks.requests.post")
        post_mock.return_value.json.return_value = expected_payload
        with pytest.raises(WebserviceException) as exception:
            get_city_council_updates()
        assert "Os parametros enviados são inválidos." in str(exception.value)

    @pytest.mark.parametrize("status_code", [400, 404, 500, 501, 503])
    def test_raise_exception_if_request_is_not_successful(self, status_code, mocker):
        post_mock = mocker.patch("datasets.tasks.requests.post")
        post_mock.return_value.status_code = status_code
        with pytest.raises(Exception):
            get_city_council_updates()


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
        sync_data_task = mocker.patch("datasets.tasks.sync_data_from_webservice.send")

        distribute_city_council_objects_to_sync(payload)

        assert sync_data_task.called is True
        assert sync_data_task.call_count == 1
        assert sync_data_task.call_args_list[0][0][0].__name__ == "update_bid"
        assert sync_data_task.call_args_list[0][0][1] == record_data

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

        sync_data_task = mocker.patch("datasets.tasks.sync_data_from_webservice")
        distribute_city_council_objects_to_sync(payload)

        assert sync_data_task.called is False
