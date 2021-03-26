import pytest


@pytest.fixture
def mock_save_file(mocker):
    pipeline_mock = mocker.patch("web.datasets.signals.pipeline")
    return pipeline_mock
