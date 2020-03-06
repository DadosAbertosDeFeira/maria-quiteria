from datasets.models import CityCouncilAgenda
from django.core.management.base import BaseCommand
from scraper.spiders.citycouncil import AgendaSpider
from scraper.spiders.utils import from_str_to_datetime
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher


class Command(BaseCommand):
    help = "Executa todos os coletores e salva os itens recentes no banco."

    def add_arguments(self, parser):
        drop_all_help = "Limpa o banco antes de inicir a coleta."
        parser.add_argument("--drop-all", action="store_true", help=drop_all_help)

    def echo(self, text, style=None):
        self.stdout.write(style(text) if style else text)

    def warn(self, text):
        return self.echo(text, self.style.WARNING)

    def success(self, text):
        return self.echo(text, self.style.SUCCESS)

    def save(self, signal, sender, item, response, spider):
        supported_formats = ["%d/%m/%Y", "%d/%m/%y"]
        CityCouncilAgenda.objects.update_or_create(
            date=from_str_to_datetime(item["date"], supported_formats).date(),
            details=item["details"],
            title=item["title"],
            event_type=item["event_type"],
        )

    def handle(self, *args, **options):
        if options.get("drop_all"):
            self.warn("Dropping existing records...")
            CityCouncilAgenda.objects.all().delete()

        dispatcher.connect(self.save, signal=signals.item_passed)
        process = CrawlerProcess(settings={"LOG_LEVEL": "INFO"})
        process.crawl(AgendaSpider)
        process.start()
        self.success("Done!")
