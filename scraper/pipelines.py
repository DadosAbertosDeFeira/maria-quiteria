from uuid import uuid4

from scrapy.http import Request
from scrapy.pipelines.files import FilesPipeline


# TODO decidir se não é melhor fazer o upload direto no S3
#  https://docs.scrapy.org/en/latest/topics/media-pipeline.html#amazon-s3-storage
class SessionAwareFilesPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        requests = super().get_media_requests(item, info)
        if item.get("file_request", None):
            request = Request(
                item["file_request"]["url"],
                dont_filter=True,
                headers=item["file_request"]["headers"],
                meta={
                    "file_path_override": f"{str(uuid4())}-{item['file_request']['filename']}"
                },
            )
            requests.append(request)
        return requests

    def file_path(self, request, response=None, info=None):
        return (
            f'full/{request.meta["file_path_override"]}'
            if "file_path_override" in request.meta
            else super().file_path(request, response, info)
        )
