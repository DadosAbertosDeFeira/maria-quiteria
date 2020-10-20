from datasets.tasks import (
    distribute_city_council_objects_to_sync,
    get_city_council_updates,
)
from django.core.management.base import BaseCommand
from dramatiq import pipeline


class Command(BaseCommand):
    help = "Dispara sincronização com o webservice da Câmara de Vereadores."

    def handle(self, *args, **options):
        pipeline(
            [
                get_city_council_updates.message(),
                distribute_city_council_objects_to_sync.message(),
            ]
        ).run()

        self.stdout.write("Syncronização com a Câmara iniciada.")
