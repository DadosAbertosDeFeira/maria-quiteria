import pytest
from model_bakery import baker


@pytest.mark.django_db
def test_backup_and_extract_content_when_file_is_saved(mock_backup_file):
    expected_link_task = "web.datasets.tasks.content_from_file"
    baker.make("datasets.File", s3_url=None, content=None)

    assert mock_backup_file.called is True
    assert mock_backup_file.call_count == 1
    assert expected_link_task in str(mock_backup_file.call_args_list[0][1]["link"])


@pytest.mark.django_db
def test_extract_content_when_file_with_backup_is_saved(mocker, mock_backup_file):
    mock_content_from_file = mocker.patch("web.datasets.tasks.content_from_file.delay")
    baker.make("datasets.File", s3_url="https://www.pdf.com/test.pdf", content=None)

    assert mock_backup_file.called is False
    assert mock_content_from_file.called is True
