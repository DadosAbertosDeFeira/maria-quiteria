from scraper.settings import FILES_STORE, KEEP_FILES
import os

from scrapy.pipelines.files import FilesPipeline
from tika import parser


class ExtractPDFContentPipeline(FilesPipeline):
    def item_completed(self, results, item, info):
        if results:
            # FIXME supports only one file by now
            file_info = results[0][1]
            file_path = f"{FILES_STORE}{file_info['path']}"
            raw = parser.from_file(file_path)
            item["file_content"] = raw["content"]
            if KEEP_FILES is False:
                os.remove(file_path)
        return item
