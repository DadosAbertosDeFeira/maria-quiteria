import os

from datasets.models import CityCouncilAgenda, Gazette, GazetteEvent
from django.core.management.base import BaseCommand
from scraper.items import CityCouncilAgendaItem, GazetteItem, LegacyGazetteItem
from scraper.spiders.citycouncil import AgendaSpider
from scraper.spiders.gazette import (
    ExecutiveAndLegislativeGazetteSpider,
    LegacyGazetteSpider,
)
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings

from ._gazette import save_gazette, save_legacy_gazette


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
        if isinstance(item, CityCouncilAgendaItem):
            CityCouncilAgenda.objects.update_or_create(
                date=item["date"],
                title=item["title"],
                event_type=item["event_type"],
                crawled_from=item["crawled_from"],
                defaults={
                    "crawled_at": item["crawled_at"],
                    "details": item["details"],
                },
            )  # TODO test it
        if isinstance(item, LegacyGazetteItem):
            save_legacy_gazette(item)
        if isinstance(item, GazetteItem):
            save_gazette(item)

    def handle(self, *args, **options):
        if options.get("drop_all"):
            self.warn("Dropping existing records...")
            CityCouncilAgenda.objects.all().delete()
            Gazette.objects.all().delete()
            GazetteEvent.objects.all().delete()

        dispatcher.connect(self.save, signal=signals.item_passed)
        os.environ["SCRAPY_SETTINGS_MODULE"] = "scraper.settings"

        process = CrawlerProcess(settings=get_project_settings())
        process.crawl(AgendaSpider)

        last_collected_gazette = Gazette.last_collected_item_date()
        if last_collected_gazette is None:
            process.crawl(LegacyGazetteSpider)
        process.crawl(
            ExecutiveAndLegislativeGazetteSpider, start_from_date=last_collected_gazette
        )

        process.start()
        self.success("Done!")
