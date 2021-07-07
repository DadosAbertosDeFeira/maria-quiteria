from web.datasets.models import File


def save_file(url, content_type, object_id, checksum=None):
    File.objects.get_or_create(
        url=url,
        content_type=content_type,
        object_id=object_id,
        checksum=checksum,
    )
