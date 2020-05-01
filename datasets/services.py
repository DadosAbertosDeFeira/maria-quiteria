from pathlib import Path

import boto3
import requests


class S3Client:
    def __init__(self, bucket, bucket_folder, bucket_region):
        self.bucket = bucket
        self.bucket_folder = bucket_folder
        self.bucket_region = bucket_region
        self.s3_resource = boto3.resource("s3")

    def upload_file(self, url, file_path, prefix=""):
        file_path = f"{self.bucket_folder}/files/{file_path}"
        temp_file_name = self.create_temp_file(url, file_path, prefix)
        file_path = f"{file_path}{temp_file_name}"

        self.s3_resource.Object(self.bucket, file_path).upload_file(
            Filename=temp_file_name
        )
        self.delete_temp_file(temp_file_name)

        url = f"https://{self.bucket}.s3.{self.bucket_region}.amazonaws.com/{file_path}"
        return url, file_path

    def download_file(self, s3_file_path):
        temporary_directory = f"{Path.cwd()}/data/tmp/"
        Path(temporary_directory).mkdir(parents=True, exist_ok=True)

        start_index = s3_file_path.rfind("/") + 1
        file_name = s3_file_path[start_index:]

        local_path = f"{temporary_directory}{file_name}"
        self.s3_resource.Object(self.bucket, s3_file_path).download_file(local_path)
        return local_path

    @staticmethod
    def create_temp_file(url, relative_file_path="", prefix=""):
        temporary_directory = f"{Path.cwd()}/data/tmp/{relative_file_path}"
        Path(temporary_directory).mkdir(parents=True, exist_ok=True)

        response = requests.get(url)
        start_index = url.rfind("/") + 1
        temp_file_name = f"{url[start_index:]}"
        if prefix:
            temp_file_name = f"{prefix}-{temp_file_name}"
        open(f"{temporary_directory}{temp_file_name}", "wb").write(response.content)
        return temp_file_name

    @staticmethod
    def delete_temp_file(temp_file_name, relative_file_path=""):
        temporary_directory = f"{Path.cwd()}/data/tmp/{relative_file_path}"
        Path(f"{temporary_directory}{temp_file_name}").unlink()


class FakeS3Client(S3Client):
    def upload_file(self, url, file_path, prefix=""):
        file_path = f"{self.bucket_folder}/files/{file_path}"
        temp_file_name = self.create_temp_file(url, file_path, prefix)
        file_path = f"{file_path}{temp_file_name}"

        url = f"https://{self.bucket}.s3.{self.bucket_region}.amazonaws.com/{file_path}"
        return url, file_path

    def download_file(self, s3_file_path):
        temporary_directory = f"{Path.cwd()}/data/tmp/"
        Path(temporary_directory).mkdir(parents=True, exist_ok=True)

        start_index = s3_file_path.rfind("/") + 1
        file_name = s3_file_path[start_index:]

        return f"{temporary_directory}{file_name}"


def get_s3_client(settings):
    use_local_file = all(
        [settings.AWS_S3_BUCKET is None, settings.AWS_S3_BUCKET_FOLDER is None]
    )

    if use_local_file:
        return FakeS3Client("teste", "maria-quiteria-local", "brasil")
    else:
        return S3Client(
            settings.AWS_S3_BUCKET,
            settings.AWS_S3_BUCKET_FOLDER,
            settings.AWS_S3_REGION,
        )
