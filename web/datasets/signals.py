from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import File


@receiver(post_save, sender=File)
def backup_and_extract_content(sender, instance, **kwargs):
    """Faz backup e extrai conteúdo de um arquivo após sua criação."""
    from .tasks import backup_file, content_from_file

    if instance.s3_url is None:
        backup_file.apply_async(
            (instance.pk,),
            link=content_from_file.si(
                instance.pk,
            ),
        )
    elif instance.content is None:
        content_from_file.delay(instance.pk)
