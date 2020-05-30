from pathlib import Path

import boto3
import requests

session = boto3.session.Session()
client = session.client("s3")


class S3Client:
    __slots__ = ("bucket", "bucket_folder", "bucket_region")

    def __init__(self, bucket, bucket_folder, bucket_region):
        self.bucket = bucket
        self.bucket_folder = bucket_folder
        self.bucket_region = bucket_region

    def upload_file(self, url, relative_file_path, prefix=""):
        bucket_file_path = f"{self.bucket_folder}/files/{relative_file_path}"
        file_name, temp_file_path = self.create_temp_file(
            url, relative_file_path, prefix
        )
        bucket_file_path = f"{bucket_file_path}{file_name}"
        url = (
            f"https://{self.bucket}.s3.{self.bucket_region}.amazonaws.com/"
            f"{bucket_file_path}"
        )
        with open(temp_file_path, "rb") as body_file:
            client.put_object(
                Bucket=self.bucket,
                Key=bucket_file_path,
                Body=body_file,
                ACL="bucket-owner-full-control",
            )

        self.delete_temp_file(temp_file_path)
        return url, bucket_file_path

    @staticmethod
    def create_temp_file(url, relative_file_path="", prefix=""):
        temporary_directory = f"{Path.cwd()}/data/tmp/{relative_file_path}"
        Path(temporary_directory).mkdir(parents=True, exist_ok=True)

        response = requests.get(url)
        start_index = url.rfind("/") + 1
        temp_file_name = f"{url[start_index:]}"
        if prefix:
            temp_file_name = f"{prefix}-{temp_file_name}"
        temp_file_path = f"{temporary_directory}{temp_file_name}"
        with open(temp_file_path, "wb") as tmp_file:
            tmp_file.write(response.content)
        return temp_file_name, temp_file_path

    def download_file(self, s3_file_path):
        temporary_directory = f"{Path.cwd()}/data/tmp/"
        Path(temporary_directory).mkdir(parents=True, exist_ok=True)

        start_index = s3_file_path.rfind("/") + 1
        file_name = s3_file_path[start_index:]

        local_path = f"{temporary_directory}{file_name}"
        with open(local_path, "wb") as file_:
            client.download_fileobj(self.bucket, s3_file_path, file_)

        return local_path

    @staticmethod
    def delete_temp_file(temp_file_path):
        Path(temp_file_path).unlink()


class FakeS3Client(S3Client):
    def upload_file(self, url, relative_file_path, prefix=""):
        file_path = f"{self.bucket_folder}/files/{relative_file_path}"
        temp_file_name, _ = self.create_temp_file(url, file_path, prefix)
        bucket_file_path = f"{file_path}{temp_file_name}"

        url = (
            f"https://{self.bucket}.s3.{self.bucket_region}.amazonaws.com/"
            f"{bucket_file_path}"
        )
        return url, bucket_file_path

    def download_file(self, s3_file_path):
        return f"{Path.cwd()}/data/tmp/{s3_file_path}"


def get_s3_client(settings):
    use_local_file = all(
        [settings.AWS_ACCESS_KEY_ID is None, settings.AWS_SECRET_ACCESS_KEY is None]
    )
    if use_local_file:
        return FakeS3Client("teste", "maria-quiteria-local", "brasil")
    else:
        return S3Client(
            settings.AWS_S3_BUCKET,
            settings.AWS_S3_BUCKET_FOLDER,
            settings.AWS_S3_REGION,
        )
