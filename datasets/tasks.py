import os
from logging import info
from pathlib import Path
from urllib.request import urlopen

import boto3
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from dramatiq import actor, set_broker
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from tika import parser

# Esse bloco (feio) faz com que esse módulo funcione dentro ou fora do Django
try:
    from datasets.models import Gazette, CityCouncilMinute, CityHallBid, File
except ImproperlyConfigured:
    import configurations

    os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    configurations.setup()
    from datasets.models import Gazette, CityCouncilMinute, CityHallBid, File


rabbitmq_broker = RabbitmqBroker(url=settings.CLOUDAMQP_URL)
set_broker(rabbitmq_broker)
ITEM_TO_MODEL = {
    "GazetteItem": Gazette,
    "LegacyGazetteItem": Gazette,
    "CityCouncilMinuteItem": CityCouncilMinute,
    "CityHallBidItem": CityHallBid,
}

AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "test-bucket")
AWS_S3_BUCKET_FOLDER = os.getenv("AWS_S3_BUCKET_FOLDER", "maria-quiteria-staging")
AWS_S3_REGION = os.getenv("AWS_S3_REGION", "test-region")

s3_resource = boto3.resource("s3")


@actor
def content_from_file(item_name, url, path, checksum, save_to_db, keep_file):
    if not Path(path).exists():
        info(f"File {path} not found.")
        return

    raw = parser.from_file(path)
    if save_to_db:
        Model = ITEM_TO_MODEL.get(item_name)
        if not Model:
            info(f"No model defined for {item_name}.")
            return
        qs = Model.objects.filter(file_url=url, file_content__isnull=True)
        qs.update(file_content=raw["content"])

    if not keep_file:
        Path(path).unlink()

    return raw["content"]


def create_temp_file(url):
    content = urlopen(url).read()
    start_index = url.rfind("/") + 1
    temp_file_name = f"{url[start_index:]}"
    open(f"{Path.cwd()}/{temp_file_name}", "wb").write(content)
    return temp_file_name


def delete_temp_file(temp_file_name):
    Path(f"{Path.cwd()}/{temp_file_name}").unlink()


@actor
def backup_file(file_id):
    try:
        file_obj = File.objects.get(pk=file_id, s3_url__isnull=True)
    except File.DoesNotExist:
        info(f"O arquivo não existe ou já possui backup {file_id}.")
        return

    model_name = file_obj.content_object._meta.model_name
    temp_file_name = create_temp_file(file_obj.url)
    file_path = (
        f"{AWS_S3_BUCKET_FOLDER}/files/{model_name}/{file_obj.created_at.year}/"
        f"{file_obj.created_at.month}/{file_obj.created_at.day}/"
        f"{file_obj.checksum}-{temp_file_name}"
    )

    s3_resource.Object(AWS_S3_BUCKET, file_path).upload_file(Filename=temp_file_name)

    s3_url = f"https://{AWS_S3_BUCKET}.s3.{AWS_S3_REGION}.amazonaws.com/" f"{file_path}"
    file_obj.s3_url = s3_url
    file_obj.save()

    delete_temp_file(temp_file_name)

    return s3_url
