import hashlib
import os

from datasets.models import CityCouncilAgenda
from scraper.items import CityCouncilAgendaItem
from scraper.settings import FILES_STORE, KEEP_FILES
from scraper.spiders.utils import from_str_to_datetime
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.python import to_bytes
from six.moves.urllib.parse import urlparse
from tika import parser


class ExtractFileContentPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None):
        """Retorna onde o arquivo foi baixado.

        Copiado de https://github.com/okfn-brasil/diario-oficial/
        Issue no scrapy: https://github.com/scrapy/scrapy/issues/4225

        de:
        8e61990b27c6158edaaa715ea76eca65459d92f4.asp?cat=PMFS&dt=03-2016
        para:
        8e61990b27c6158edaaa715ea76eca65459d92f4.asp
        """
        url = request.url
        media_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        media_ext = os.path.splitext(url)[1]
        if not media_ext.isalnum():
            media_ext = os.path.splitext(urlparse(url).path)[1]
        return "full/%s%s" % (media_guid, media_ext)

    def item_completed(self, results, item, info):
        if results and results[0][0]:
            file_info = results[0][1]
            file_path = f"{FILES_STORE}{file_info['path']}"
            raw = parser.from_file(file_path)
            item["file_content"] = raw["content"]
            if KEEP_FILES is False:
                os.remove(file_path)
        return item


class CityCouncilAgendaPipeline(object):
    def process_item(self, item, spider):
        if not isinstance(item, CityCouncilAgendaItem):
            return item

        supported_formats = ["%d/%m/%Y", "%d/%m/%y"]
        CityCouncilAgenda.objects.update_or_create(
            date=from_str_to_datetime(item["date"], supported_formats).date(),
            details=item["details"],
            title=item["title"],
            event_type=item["event_type"],
        )

        return item
