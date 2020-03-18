import pytest
from model_bakery import baker

from scraper.settings import FILES_STORE, KEEP_FILES
from datasets.models import Gazette
from datasets.tasks import content_from_file


@pytest.mark.django_db
def test_extract_content_from_files(mocker):
    url = "https://maria.quiteria/fourty.two"
    baker.make(Gazette, file_url=url)
    path = mocker.patch("datasets.tasks.Path")
    parser = mocker.patch("datasets.tasks.parser")
    parser.from_file.return_value = {"content": "fourty-two"}

    content_from_file(path="/fourty.two", url=url, checksum="f42")

    parser.from_file.assert_called_once_with(f"{FILES_STORE}/fourty.two")
    if KEEP_FILES:
        path.return_value.unlink.assert_not_called()
    else:
        path.return_value.unlink.assert_called_once_with()
    assert Gazette.objects.get(file_url=url).file_content == "fourty-two"
