from datasets.models import File
from datasets.tasks import backup_file, content_from_file
from dramatiq import pipeline


def save_file(url, content_type, object_id):
    # FIXME checksum
    file_, created = File.objects.get_or_create(
        url=url, content_type=content_type, object_id=object_id
    )
    if file_.s3_url is None or file_.content is None:
        pipeline(
            [
                backup_file.message(file_.pk),
                content_from_file.message_with_options(
                    pipe_ignore=True, args=(file_.pk,)
                ),
            ]
        ).run()
