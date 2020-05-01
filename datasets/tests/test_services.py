import os
from pathlib import Path

from datasets.services import get_s3_client
from django.conf import settings

client = get_s3_client(settings)


class TestS3Client:
    def test_upload_file(self):
        relative_path = "TestModel/2020/10/23/"
        s3_url, file_path = client.upload_file(
            "https://www.google.com/robots.txt", relative_path
        )

        expected_file_path = f"maria-quiteria-local/files/{relative_path}robots.txt"
        expected_s3_url = f"https://teste.s3.brasil.amazonaws.com/{expected_file_path}"
        real_path = f"{os.getcwd()}/data/tmp/{expected_file_path}"

        assert s3_url == expected_s3_url
        assert file_path == expected_file_path
        assert Path(real_path).exists()

        client.delete_temp_file(expected_file_path)

    def test_create_temp_file(self):
        url = (
            "http://www.feiradesantana.ba.gov.br/licitacoes/"
            "respostas/4924SUSPENS%C3%83O.pdf"
        )
        temp_file_name = client.create_temp_file(url)

        assert temp_file_name == "4924SUSPENS%C3%83O.pdf"
        assert Path(f"{Path.cwd()}/data/tmp/4924SUSPENS%C3%83O.pdf").is_file() is True

        client.delete_temp_file("4924SUSPENS%C3%83O.pdf")
        assert Path(f"{Path.cwd()}/data/tmp/4924SUSPENS%C3%83O.pdf").is_file() is False

    def test_create_temp_file_with_prefix(self):
        url = (
            "http://www.feiradesantana.ba.gov.br/licitacoes/"
            "respostas/4924SUSPENS%C3%83O.pdf"
        )
        prefix = "eu-sou-um-checksum"
        expected_file_name = f"{prefix}-4924SUSPENS%C3%83O.pdf"
        temp_file_name = client.create_temp_file(url, prefix=prefix)

        assert temp_file_name == expected_file_name
        assert Path(f"{Path.cwd()}/data/tmp/{expected_file_name}").is_file() is True

        client.delete_temp_file(expected_file_name)
        assert Path(f"{Path.cwd()}/data/tmp/{expected_file_name}").is_file() is False

    def test_create_temp_file_with_relative_file_path(self):  # FIXME
        url = (
            "http://www.feiradesantana.ba.gov.br/licitacoes/"
            "respostas/4924SUSPENS%C3%83O.pdf"
        )
        relative_file_path = "extra/"
        temp_file_name = client.create_temp_file(
            url, relative_file_path=relative_file_path
        )

        assert temp_file_name == "4924SUSPENS%C3%83O.pdf"
        assert (
            Path(f"{Path.cwd()}/data/tmp/extra/4924SUSPENS%C3%83O.pdf").is_file()
            is True
        )

        client.delete_temp_file(
            "4924SUSPENS%C3%83O.pdf", relative_file_path=relative_file_path
        )
        assert (
            Path(f"{Path.cwd()}/data/tmp/extra/4924SUSPENS%C3%83O.pdf").is_file()
            is False
        )
