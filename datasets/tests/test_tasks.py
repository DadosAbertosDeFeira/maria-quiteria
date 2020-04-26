from pathlib import Path

import pytest
from datasets.models import Gazette
from datasets.tasks import (
    backup_file,
    content_from_file,
    create_temp_file,
    delete_temp_file,
)
from model_bakery import baker


def test_content_from_files_not_saving_to_db(mocker):
    url = "https://maria.quiteria/quarenta-e-dois.pdf"
    path = "full/42.pdf"

    path = mocker.patch("datasets.tasks.Path")
    parser = mocker.patch("datasets.tasks.parser")
    parser.from_file.return_value = {"content": "quarenta e dois"}

    result = content_from_file("GazetteItem", url, path, "f42", False, False)
    parser.from_file.assert_called_once_with(path)
    path.return_value.unlink.assert_called_once_with()
    assert result == "quarenta e dois"


@pytest.mark.django_db
def test_content_from_files_saving_to_db(mocker):
    url = "https://maria.quiteria/quarenta-e-dois.pdf"
    path = "full/42.pdf"
    baker.make(Gazette, file_url=url)

    path = mocker.patch("datasets.tasks.Path")
    parser = mocker.patch("datasets.tasks.parser")
    parser.from_file.return_value = {"content": "quarenta e dois"}

    result = content_from_file("GazetteItem", url, path, "f42", True, True)
    parser.from_file.assert_called_once_with(path)
    path.return_value.unlink.assert_not_called()
    assert Gazette.objects.get(file_url=url).file_content == "quarenta e dois"
    assert result == "quarenta e dois"


@pytest.mark.django_db
def test_backup_file(mocker):
    url = "http://www.feiradesantana.ba.gov.br/licitacoes/4914pmfspp2182019.pdf"
    gazette = baker.make("datasets.Gazette")
    a_file = baker.make(
        "datasets.File", url=url, content_object=gazette, checksum="random"
    )

    expected_s3_url = (
        "https://test-bucket.s3.test-region.amazonaws.com/maria-quiteria-staging/"
        "files/gazette/2020/4/26/random-4914pmfspp2182019.pdf"
    )
    boto3_mock = mocker.patch("datasets.tasks.s3_resource.Object")

    backup_file(a_file.pk)

    assert boto3_mock.called
    a_file.refresh_from_db()

    assert a_file.s3_url == expected_s3_url


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
