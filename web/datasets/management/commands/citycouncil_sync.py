from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand
from dramatiq import pipeline
from web.datasets.tasks import (
    distribute_city_council_objects_to_sync,
    get_city_council_updates,
)


class Command(BaseCommand):
    help = "Dispara sincronização com o webservice da Câmara de Vereadores."

    def add_arguments(self, parser):
        parser.add_argument("--date", help="Data no formato aaaa-mm-dd")

    def handle(self, *args, **options):
        if options.get("date"):
            # converte para datetime para verificar se o formato está correto
            target_date = datetime.strptime(options.get("date"), "%Y-%m-%d").date()
        else:
            # ontem
            target_date = date.today() - timedelta(days=1)
        pipeline(
            [
                get_city_council_updates.message(target_date.strftime("%Y-%m-%d")),
                distribute_city_council_objects_to_sync.message(),
            ]
        ).run()

        self.stdout.write(
            f"Syncronização com a Câmara iniciada (data alvo: {target_date})."
        )
