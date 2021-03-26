import pytest
from model_bakery import baker


@pytest.mark.django_db
def test_backup_and_extract_content_when_file_is_saved(mock_save_file):
    baker.make("datasets.File", s3_url=None, content=None)

    assert mock_save_file.called is True
    assert mock_save_file.call_args_list[0][0][0][0].actor_name == "backup_file"
    assert mock_save_file.call_args_list[0][0][0][1].actor_name == "content_from_file"
