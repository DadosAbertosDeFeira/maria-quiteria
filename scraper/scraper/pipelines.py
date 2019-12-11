from scraper.settings import FILES_STORE
import os

from scrapy.pipelines.files import FilesPipeline
from tika import parser


class ExtractPDFContentPipeline(FilesPipeline):
    def item_completed(self, results, item, info):
        file_info = results[0][1]
        file_path = f"{FILES_STORE}{file_info['path']}"
        raw = parser.from_file(file_path)
        item["content"] = raw["content"]
        os.remove(file_path)  # TODO add env variable for it
        return item
