from datasets.models import File
from django.contrib.postgres.search import SearchVector
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """Remonta os indices de busca e diários em caso de problemas
            com a geração de índice via trigger"""

    def echo(self, text, style=None):
        self.stdout.write(style(text) if style else text)

    def handle(self, *args, **options):
        file_count = File.objects.count()
        self.echo(
            f"Criando um vetor de busca para os arquivos. "
            f"Total de itens: {file_count:,}",
            self.style.SUCCESS,
        )
        self.echo("Aguarde...", self.style.SUCCESS)

        search_vector = SearchVector("file_content", config="portuguese")

        File.objects.update(search_vector=search_vector)

        self.echo("Pronto!", self.style.SUCCESS)
