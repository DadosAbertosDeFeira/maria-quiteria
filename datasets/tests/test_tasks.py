from pathlib import Path

import pytest
from datasets.tasks import (
    backup_file,
    content_from_file,
    create_temp_file,
    delete_temp_file,
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
    path_mock.return_value.mkdir.return_value = True
    path_mock.return_value.exists.return_value = True
    path_mock.return_value.unlink.return_value = True
    return path_mock


@pytest.fixture
def s3(mocker):
    return mocker.patch("datasets.tasks.s3_resource.Object")


@pytest.mark.django_db
def test_content_from_file_saved_to_db(parser, path, s3):
    gazette = baker.make("datasets.Gazette")
    a_file = baker.make(
        "datasets.File",
        url="https://url.com",
        content_object=gazette,
        checksum="random",
        s3_url="https://dadosabertosdefeira.com/mq/Termo_de_Referência_-_HOSP_CAMP.pdf",
        s3_file_path="mq/Termo_de_Referência_-_HOSP_CAMP.pdf",
        content=None,
    )

    result = content_from_file(a_file.pk)

    assert s3.called

    a_file.refresh_from_db()
    assert a_file.content == "quarenta e dois"
    assert result == "quarenta e dois"

    assert parser.from_file.called
    assert path().unlink.called


def test_content_from_files_not_saving_to_db(parser, path):
    result = content_from_file(path="/tmp/README.md")

    assert parser.from_file.called
    assert path().unlink.called is False

    assert result == "quarenta e dois"


@pytest.mark.django_db
def test_backup_file(s3):
    url = "http://www.feiradesantana.ba.gov.br/licitacoes/4914pmfspp2182019.pdf"
    gazette = baker.make("datasets.Gazette")
    a_file = baker.make(
        "datasets.File", url=url, content_object=gazette, checksum="random"
    )
    expected_s3_file_path = (
        f"None/files/gazette/{a_file.created_at.year}/{a_file.created_at.month}/"
        f"{a_file.created_at.day}/random-4914pmfspp2182019.pdf"
    )
    expected_s3_url = f"https://None.s3.None.amazonaws.com/{expected_s3_file_path}"

    backup_file(a_file.pk)

    assert s3.called
    a_file.refresh_from_db()

    assert a_file.s3_url == expected_s3_url
    assert a_file.s3_file_path == expected_s3_file_path


@pytest.mark.django_db
def test_return_none_when_file_does_not_exist():
    assert backup_file(9) is None


@pytest.mark.django_db
def test_return_none_when_file_has_backup_already():
    gazette = baker.make("datasets.Gazette")
    a_file = baker.make(
        "datasets.File",
        url="https://url.com",
        content_object=gazette,
        checksum="random",
        s3_url="https://s3url.com",
    )
    assert backup_file(a_file.pk) is None


def test_create_temp_file():
    url = "http://www.feiradesantana.ba.gov.br/licitacoes/4914pmfspp2182019.pdf"
    temp_file_name = create_temp_file(url)

    assert temp_file_name == "4914pmfspp2182019.pdf"
    assert Path(f"{Path.cwd()}/4914pmfspp2182019.pdf").is_file() is True

    delete_temp_file("4914pmfspp2182019.pdf")
    assert Path(f"{Path.cwd()}/4914pmfspp2182019.pdf").is_file() is False
