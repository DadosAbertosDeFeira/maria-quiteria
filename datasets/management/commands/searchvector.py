from django.contrib.postgres.search import SearchVector
from django.core.management.base import BaseCommand

from datasets.models import Gazette


class Command(BaseCommand):
    help = """Remonta os indices de busca e diários em caso de problemas
            com a geração de índice via trigger"""

    def echo(self, text, style=None):
        self.stdout.write(style(text) if style else text)

    def handle(self, *args, **options):
        gazette_count = Gazette.objects.count()
        self.echo(
            f"Creating search vector for Gazette. Total items: {gazette_count:,}",
            self.style.SUCCESS,
        )
        self.echo("Please wait...", self.style.SUCCESS)

        search_vector = SearchVector("file_content", config="portuguese")

        Gazette.objects.update(search_vector=search_vector)

        self.echo("Done!", self.style.SUCCESS)
