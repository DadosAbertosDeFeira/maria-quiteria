import pytest


@pytest.fixture
def mock_save_file(mocker, monkeypatch):
    monkeypatch.setenv("ENABLE_SIGNAL_FOR_FILE_TASKS", True)
    pipeline_mock = mocker.patch("web.datasets.signals.pipeline")
    return pipeline_mock
