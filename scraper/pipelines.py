from hashlib import sha1
from pathlib import Path
from urllib.parse import urlparse

from datasets.tasks import content_from_file
from scraper.settings import ASYNC_FILE_PROCESSING, FILES_STORE, KEEP_FILES
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.python import to_bytes


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
            return item

        content_from_file_urls = []
        for result in results:
            ok, file_info = result
            if not ok:
                continue

            kwargs = {
                "item_name": item.__class__.__name__,
                "url": file_info["url"],
                "path": f"{FILES_STORE}{file_info['path']}",
                "checksum": file_info["checksum"],
                "save_to_db": ASYNC_FILE_PROCESSING,
                "keep_file": KEEP_FILES,
            }
            if ASYNC_FILE_PROCESSING:
                # TODO file url
                # TODO download e extração do conteúdo do arquivo
                content_from_file.send(**kwargs)
            else:
                content_from_file_urls.append(content_from_file(**kwargs))
        item["file_content"] = content_from_file_urls
        return item
