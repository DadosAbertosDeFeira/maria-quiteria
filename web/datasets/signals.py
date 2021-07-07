import os

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import File


@receiver(post_save, sender=File)
def backup_and_extract_content(sender, instance, **kwargs):
    """Faz backup e extrai conteúdo de um arquivo após sua criação."""
    if bool(os.getenv("ENABLE_SIGNAL_FOR_FILE_TASKS", False)):
        from .tasks import backup_file, content_from_file

        if instance.s3_url is None or instance.content is None:
            backup_file.apply_async(
                (instance.pk,),
                link=content_from_file.s(
                    instance.pk,
                ),
            )
