import pytest
from model_bakery import baker

from datasets.models import Gazette
from datasets.tasks import content_from_file


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
    assert Gazette.objects.get(file_url=url).checksum == "f42"
    assert result == "quarenta e dois"
