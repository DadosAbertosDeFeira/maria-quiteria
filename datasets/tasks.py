from logging import info
from pathlib import Path

import boto3
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from dramatiq import actor, set_broker
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from tika import parser

# Esse bloco (feio) faz com que esse módulo funcione dentro ou fora do Django
try:
    from datasets.models import File
except ImproperlyConfigured:
    import configurations
    import os

    os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    configurations.setup()
    from datasets.models import File


rabbitmq_broker = RabbitmqBroker(url=settings.CLOUDAMQP_URL)
set_broker(rabbitmq_broker)
s3_resource = boto3.resource("s3")  # TODO criar stub?

AWS_S3_BUCKET = settings.AWS_S3_BUCKET
AWS_S3_BUCKET_FOLDER = settings.AWS_S3_BUCKET_FOLDER
AWS_S3_REGION = settings.AWS_S3_REGION


@actor
def content_from_file(file_pk=None, path=None, keep_file=True):
    if not any([file_pk, path]):
        raise Exception("Ou `file_pk` ou `path` devem ser informados.")

    a_file = None
    if file_pk:
        a_file = File.objects.get(pk=file_pk)

        temporary_directory = f"{Path.cwd()}/data/tmp/"
        Path(temporary_directory).mkdir(parents=True, exist_ok=True)

        start_index = a_file.s3_url.rfind("/") + 1
        file_name = a_file.s3_url[start_index:]

        path = f"{temporary_directory}{file_name}"

        s3_resource.Object(AWS_S3_BUCKET, a_file.s3_file_path).download_file(path)

        keep_file = False

    if not Path(path).exists():
        info(f"Arquivo {path} não encontrado.")
        return

    raw = parser.from_file(path)

    if not keep_file:
        Path(path).unlink()

    if a_file:
        a_file.content = raw["content"]
        a_file.save()

    return raw["content"]


def create_temp_file(url):
    response = requests.get(url)
    start_index = url.rfind("/") + 1
    temp_file_name = f"{url[start_index:]}"
    open(f"{Path.cwd()}/{temp_file_name}", "wb").write(response.content)
    return temp_file_name


def delete_temp_file(temp_file_name):
    Path(f"{Path.cwd()}/{temp_file_name}").unlink()


@actor
def backup_file(file_id):
    try:
        file_obj = File.objects.get(pk=file_id, s3_url__isnull=True)
    except File.DoesNotExist:
        info(f"O arquivo ({file_id}) não existe ou já possui backup.")
        return

    model_name = file_obj.content_object._meta.model_name
    temp_file_name = create_temp_file(file_obj.url)
    file_path = (
        f"{AWS_S3_BUCKET_FOLDER}/files/{model_name}/{file_obj.created_at.year}/"
        f"{file_obj.created_at.month}/{file_obj.created_at.day}/"
        f"{file_obj.checksum}-{temp_file_name}"
    )

    s3_resource.Object(AWS_S3_BUCKET, file_path).upload_file(Filename=temp_file_name)

    s3_url = f"https://{AWS_S3_BUCKET}.s3.{AWS_S3_REGION}.amazonaws.com/{file_path}"
    file_obj.s3_file_path = file_path
    file_obj.s3_url = s3_url
    file_obj.save()

    delete_temp_file(temp_file_name)

    return s3_url
