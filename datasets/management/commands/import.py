import csv

from datasets.adapters import to_expense
from datasets.models import CityCouncilExpense
from django.core.management.base import BaseCommand

mapping = {
    "citycouncil_expenses": {"model": CityCouncilExpense, "adapter": to_expense,},
}


class Command(BaseCommand):
    help = "Importa dados de um arquivo CSV."

    def add_arguments(self, parser):
        parser.add_argument("source")
        parser.add_argument("file")

    def echo(self, text, style=None):
        self.stdout.write(style(text) if style else text)

    def warn(self, text):
        return self.echo(text, self.style.WARNING)

    def success(self, text):
        return self.echo(text, self.style.SUCCESS)

    def handle(self, *args, **options):
        self.warn(options.get("source"))
        self.warn(options.get("file"))

        source_map = mapping.get(options.get("source"))

        with open(options.get("file"), newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                item = source_map["adapter"](row)
                # TODO salvar
