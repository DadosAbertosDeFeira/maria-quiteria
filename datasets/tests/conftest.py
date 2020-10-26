import pytest


@pytest.fixture
def mock_save_file(mocker, settings):
    pipeline_mock = mocker.patch("datasets.signals.pipeline")
    return pipeline_mock
