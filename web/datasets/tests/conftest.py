import pytest


@pytest.fixture
def mock_save_file(mocker):
    return mocker.patch("web.datasets.tasks.backup_file.apply_async")
