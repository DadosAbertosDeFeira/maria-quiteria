import pytest
from model_bakery import baker


@pytest.mark.django_db
def test_backup_and_extract_content_when_file_is_saved(mock_save_file):
    expected_link_task = "web.datasets.tasks.content_from_file"
    baker.make("datasets.File", s3_url=None, content=None)

    assert mock_save_file.called is True
    assert mock_save_file.call_count == 1
    assert expected_link_task in str(mock_save_file.call_args_list[0][1]["link"])
