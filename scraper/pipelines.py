from hashlib import sha1
from pathlib import Path
from urllib.parse import urlparse

from datasets.tasks import content_from_file
from scraper.settings import EXTRACT_FILE_CONTENT_FROM_PIPELINE, FILES_STORE, KEEP_FILES
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

        files = []
        for result in results:
            ok, file_info = result
            if not ok:
                continue

            if EXTRACT_FILE_CONTENT_FROM_PIPELINE:
                kwargs = {
                    "path": f"{FILES_STORE}{file_info['path']}",
                    "keep_file": KEEP_FILES,
                }
                content = content_from_file(**kwargs)
            else:
                content = None
            files.append(
                {
                    "url": file_info["url"],
                    "checksum": file_info["checksum"],
                    "content": content,
                }
            )
        item["files"] = files
        del item["file_urls"]

        return item
