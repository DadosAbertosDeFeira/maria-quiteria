from datetime import date, datetime, timedelta

from celery import chain
from django.core.management.base import BaseCommand
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

        chain(
            get_city_council_updates.s(target_date.strftime("%Y-%m-%d")),
            distribute_city_council_objects_to_sync.s(),
        )()

        self.stdout.write(
            f"Syncronização com a Câmara iniciada (data alvo: {target_date})."
        )
