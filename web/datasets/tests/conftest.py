import pytest


@pytest.fixture
def mock_save_file(mocker):
    parser_mock = mocker.patch("web.datasets.management.commands._file.pipeline")
    return parser_mock
