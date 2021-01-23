import csv
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from web.datasets.adapters import (
    to_bid,
    to_bid_file,
    to_contract,
    to_contract_file,
    to_expense,
    to_revenue,
)
from web.datasets.models import (
    CityCouncilBid,
    CityCouncilContract,
    CityCouncilExpense,
    CityCouncilRevenue,
    File,
)

mapping = {
    "citycouncil_expenses": {"model": CityCouncilExpense, "adapter": to_expense},
    "citycouncil_contracts": {"model": CityCouncilContract, "adapter": to_contract},
    "citycouncil_bids": {"model": CityCouncilBid, "adapter": to_bid},
    "citycouncil_revenue": {"model": CityCouncilRevenue, "adapter": to_revenue},
    "citycouncil_contract_files": {"model": File, "adapter": to_contract_file},
    "citycouncil_bid_files": {"model": File, "adapter": to_bid_file},
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
            confirmation = input("Tem certeza? s/n")
            if confirmation.lower() in ["s", "y"]:
                model.objects.all().delete()

        saved = 0
        errors = 0
        with open(options.get("file"), newline="") as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                item = adapter(row)
                if not options.get("source").endswith("_files"):
                    item.crawled_at = datetime.now()
                    item.crawled_from = settings.CITY_COUNCIL_WEBSERVICE
                try:
                    item.save()
                    saved += 1
                except Exception as e:
                    errors += 1
                    self.warn(f"{e}\n{str(row)}")

        self.success(f"Concluído!\nSalvos: {saved} Erros: {errors}")
