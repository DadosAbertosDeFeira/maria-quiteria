import csv
import os
from datetime import datetime

from datasets.models import CityCouncilBid, CityCouncilContract, CityCouncilExpense
from datasets.webservices.adapters import to_bid, to_contract, to_expense
from django.core.management.base import BaseCommand

mapping = {
    "citycouncil_expenses": {"model": CityCouncilExpense, "adapter": to_expense},
    "citycouncil_contracts": {"model": CityCouncilContract, "adapter": to_contract},
    "citycouncil_bids": {"model": CityCouncilBid, "adapter": to_bid},
}


class Command(BaseCommand):
    help = "Importa dados de um arquivo CSV."

    def add_arguments(self, parser):
        parser.add_argument("source")
        parser.add_argument("file")
        parser.add_argument("--drop-all", action="store_true")

    def echo(self, text, style=None):
        self.stdout.write(style(text) if style else text)

    def warn(self, text):
        return self.echo(text, self.style.WARNING)

    def success(self, text):
        return self.echo(text, self.style.SUCCESS)

    def handle(self, *args, **options):
        self.echo(options.get("source"))
        self.echo(options.get("file"))

        source_map = mapping.get(options.get("source"))
        adapter = source_map["adapter"]
        model = source_map["model"]

        if options.get("drop_all"):
            model.objects.all().delete()

        with open(options.get("file"), newline="") as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                item = adapter(row)
                item.crawled_at = datetime.now()
                item.crawled_from = os.getenv("CITY_COUNCIL_WEBSERVICE")
                try:
                    item.save()
                except Exception as e:
                    self.warn(f"{e}\n{str(row)}")

        self.success("Concluído!")
