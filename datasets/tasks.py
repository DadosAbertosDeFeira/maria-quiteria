from logging import info
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from dramatiq import actor
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from tika import parser

# Esse bloco (feio) faz com que esse módulo funcione dentro ou fora do Django
try:
    from datasets.models import Gazette
except ImproperlyConfigured:
    import os
    import configurations

    os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    configurations.setup()
    from datasets.models import Gazette


RabbitmqBroker(url=settings.CLOUDAMQP_URL)
ITEM_TO_MODEL = {"GazetteItem": Gazette, "LegacyGazetteItem": Gazette}


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
        qs.update(file_content=raw["content"], checksum=checksum)

    if not keep_file:
        Path(path).unlink()

    return raw["content"]
