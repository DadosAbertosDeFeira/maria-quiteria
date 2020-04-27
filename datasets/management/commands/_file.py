from datasets.models import File
from datasets.tasks import backup_file


def save_file(url, content_type, object_id):
    # FIXME checksum
    file_, created = File.objects.get_or_create(
        url=url, content_type=content_type, object_id=object_id
    )
    if created:
        backup_file.send(file_.pk)
