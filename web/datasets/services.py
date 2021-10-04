import os
from pathlib import Path

import boto3
import requests
from django.conf import settings


class S3Client:
    __slots__ = ("client", "bucket", "bucket_folder", "bucket_region")

    def __init__(self, client, bucket, bucket_folder, bucket_region):
        self.client = client
        self.bucket = bucket
        self.bucket_folder = bucket_folder
        self.bucket_region = bucket_region

    def _upload_to_s3(self, temp_file_path, bucket_file_path):
        with open(temp_file_path, "rb") as body_file:
            self.client.put_object(
                Bucket=self.bucket,
                Key=bucket_file_path,
                Body=body_file,
            )

    def upload_file(self, location_or_url, relative_file_path, prefix=""):
        bucket_file_path = f"{self.bucket_folder}/files/{relative_file_path}"

        location = Path(location_or_url)
        if not location.exists():
            # se não é um arquivo local, assumimos que é uma url
            file_name, temp_file_path = self.create_temp_file(
                location_or_url, bucket_file_path, prefix
            )
        else:
            file_name, temp_file_path = location.name, str(location.absolute())

        bucket_file_path = f"{bucket_file_path}/{file_name}"
        url = (
            f"https://{self.bucket}.s3.{self.bucket_region}.amazonaws.com/"
            f"{bucket_file_path}"
        )
        self._upload_to_s3(temp_file_path, bucket_file_path)
        self.delete_temp_file(temp_file_path)

        return url, bucket_file_path

    @staticmethod
    def create_temp_file(url, relative_file_path="", prefix=""):
        temporary_directory = Path(f"{settings.DATA_DIR}/{relative_file_path}")
        temporary_directory.mkdir(parents=True, exist_ok=True)

        response = requests.get(url)
        start_index = url.rfind("/") + 1
        temp_file_name = f"{url[start_index:]}"
        if prefix:
            temp_file_name = f"{prefix}-{temp_file_name}"
        temp_file_path = temporary_directory / temp_file_name

        temp_file_path.write_bytes(response.content)
        return temp_file_name, str(temp_file_path.absolute())

    def download_file(self, s3_file_path):
        Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)

        start_index = s3_file_path.rfind("/") + 1
        file_name = s3_file_path[start_index:]

        local_path = f"{settings.DATA_DIR}/{file_name}"
        with open(local_path, "wb") as file_:
            self.client.download_fileobj(self.bucket, s3_file_path, file_)

        return local_path

    @staticmethod
    def delete_temp_file(temp_file_path):
        Path(temp_file_path).unlink()


class FakeS3Client(S3Client):
    def _upload_to_s3(self, temp_file_path, bucket_file_path):
        pass

    def download_file(self, s3_file_path):
        return f"{settings.DATA_DIR}/{s3_file_path}"

    @staticmethod
    def delete_temp_file(temp_file_path):
        pass


def get_s3_client(settings):
    if os.getenv("DJANGO_CONFIGURATION") != "Prod":
        from unittest.mock import Mock

        client = Mock()
        return FakeS3Client(client, "teste", "maria-quiteria-local", "brasil")

    client = boto3.client(
        service_name="s3",
        region_name=settings.AWS_S3_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    return S3Client(
        client,
        settings.AWS_S3_BUCKET,
        settings.AWS_S3_BUCKET_FOLDER,
        settings.AWS_S3_REGION,
    )
