from logging import info
from pathlib import Path

from dramatiq import actor
from scraper.settings import ASYNC_FILE_DOWLOAD, FILES_STORE, KEEP_FILES
from tika import parser

from datasets.models import Gazette


ITEM_TO_MODEL = {
    "GazetteItem": Gazette,
    "LegacyGazetteItem": Gazette
}


@actor
def content_from_file(item_name, url, path, checksum):
    if not Path(path).exists():
        info(f"File {path} not found.")
        return

    Model = ITEM_TO_MODEL.get(item_name)
    if not Model:
        info(f"No model defined for {item_name}.")
        return

    raw = parser.from_file(f"{FILES_STORE}{path}")
    if ASYNC_FILE_DOWLOAD:
        qs = Model.objects.filter(file_url=url, file_content__isnull=True)
        qs.update(file_content=raw["content"], checksum=checksum)

    if not KEEP_FILES:
        Path(path).unlink()

    return raw["content"]
