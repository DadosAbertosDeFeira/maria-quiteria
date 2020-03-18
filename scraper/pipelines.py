from hashlib import sha1
from pathlib import Path
from urllib.parse import urlparse

from scraper.settings import ASYNC_FILE_DOWLOAD
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.python import to_bytes

from datasets.tasks import content_from_file


class ExtractFileContentPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None):
        """Retorna um nome único para o arquivo foi baixado, removendo
        parâmetros da URL. Por exemplo:

        de:
        8e61990b27c6158edaaa715ea76eca65459d92f4.asp?cat=PMFS&dt=03-2016
        para:
        8e61990b27c6158edaaa715ea76eca65459d92f4.asp


        Issue no scrapy: https://github.com/scrapy/scrapy/issues/4225
        """
        uid = sha1(to_bytes(request.url)).hexdigest()
        extension = Path(urlparse(request.url).path).suffix
        return f"full/{uid}{extension}"

    def item_completed(self, results, item, info):
        if not results:
            return

        for result in results:
            ok, file_info = result
            if not ok:
                continue

            if ASYNC_FILE_DOWLOAD:
                content_from_file.send(item.__name__, **file_info)
            else:
                content = content_from_file(item.__name__, **file_info)
                item["file_content"] = content

            yield item
