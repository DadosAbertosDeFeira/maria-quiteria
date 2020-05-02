import os
from pathlib import Path

from datasets.services import get_s3_client
from django.conf import settings

client = get_s3_client(settings)


class TestS3Client:
    def test_upload_file(self):
        relative_path = "TestModel/2020/10/23/"
        s3_url, bucket_file_path = client.upload_file(
            "https://www.google.com/robots.txt", relative_path
        )

        expected_file_path = f"maria-quiteria-local/files/{relative_path}robots.txt"
        expected_s3_url = f"https://teste.s3.brasil.amazonaws.com/{bucket_file_path}"
        real_path = f"{os.getcwd()}/data/tmp/{expected_file_path}"

        assert s3_url == expected_s3_url
        assert bucket_file_path == expected_file_path
        assert Path(real_path).exists()

        client.delete_temp_file(real_path)

    def test_create_temp_file(self):
        url = (
            "http://www.feiradesantana.ba.gov.br/licitacoes/"
            "respostas/4924SUSPENS%C3%83O.pdf"
        )
        temp_file_name, temp_file_path = client.create_temp_file(url)

        assert temp_file_name == "4924SUSPENS%C3%83O.pdf"
        assert Path(temp_file_path).is_file() is True

        client.delete_temp_file(temp_file_path)
        assert Path(temp_file_path).is_file() is False

    def test_create_temp_file_with_prefix(self):
        url = (
            "http://www.feiradesantana.ba.gov.br/licitacoes/"
            "respostas/4924SUSPENS%C3%83O.pdf"
        )
        prefix = "eu-sou-um-checksum"
        expected_file_name = f"{prefix}-4924SUSPENS%C3%83O.pdf"
        temp_file_name, temp_file_path = client.create_temp_file(url, prefix=prefix)

        assert temp_file_name == expected_file_name
        assert Path(temp_file_path).is_file() is True

        client.delete_temp_file(temp_file_path)
        assert Path(temp_file_path).is_file() is False

    def test_create_temp_file_with_relative_file_path(self):
        url = (
            "http://www.feiradesantana.ba.gov.br/licitacoes/"
            "respostas/4924SUSPENS%C3%83O.pdf"
        )
        relative_file_path = "extra/"
        temp_file_name, temp_file_path = client.create_temp_file(
            url, relative_file_path=relative_file_path
        )

        assert temp_file_name == "4924SUSPENS%C3%83O.pdf"
        assert Path(temp_file_path).is_file() is True

        client.delete_temp_file(temp_file_path)

        assert Path(temp_file_path).is_file() is False

    def test_download_file(self):
        relative_path = "TestModel/2020/10/23/"
        s3_url, relative_file_path = client.upload_file(
            "https://www.google.com/robots.txt", relative_path
        )

        expected_file_path = f"maria-quiteria-local/files/{relative_path}robots.txt"
        expected_s3_url = f"https://teste.s3.brasil.amazonaws.com/{expected_file_path}"
        real_path = f"{os.getcwd()}/data/tmp/{expected_file_path}"

        assert s3_url == expected_s3_url
        assert relative_file_path == expected_file_path
        assert Path(real_path).exists()

        absolute_file_path = client.download_file(relative_file_path)

        assert absolute_file_path == real_path

        client.delete_temp_file(absolute_file_path)
