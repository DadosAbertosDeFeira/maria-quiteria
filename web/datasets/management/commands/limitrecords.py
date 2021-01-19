from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Limita os registros no banco de dados.

    Feito para ser executado diariamente em ambientes de testes que utilizem
    a versão gratuita do Postgres no Heroku (limitado a 10000 registros).
    """

    help = "Limita registros a serem mantidos no banco de dados."

    def echo(self, text, style=None):
        self.stdout.write(style(text) if style else text)

    def warn(self, text):
        return self.echo(text, self.style.WARNING)

    def success(self, text):
        return self.echo(text, self.style.SUCCESS)

    def handle(self, *args, **options):
        limit = 1000
        for label, model in apps.all_models["datasets"].items():
            all_records = model.objects.all().order_by("pk")
            total = all_records.count()

            if total >= limit:
                deleted = 0
                for to_be_deleted in all_records[: total - 1000]:
                    to_be_deleted.delete()
                    deleted += 1
                self.warn(f"{label} ({total} -> {total - deleted})")
            else:
                self.warn(f"{label} ({total})")
        self.success("Feito.")
