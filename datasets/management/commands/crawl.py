import os

from datasets.models import (
    CityCouncilAgenda,
    CityCouncilAttendanceList,
    CityCouncilMinute,
    CityHallBid,
    Gazette,
    GazetteEvent,
)
from django.core.management.base import BaseCommand
from scraper.items import (
    CityCouncilAgendaItem,
    CityCouncilAttendanceListItem,
    CityCouncilMinuteItem,
    CityHallBidItem,
    GazetteItem,
    LegacyGazetteItem,
)
from scraper.spiders.citycouncil import AgendaSpider, AttendanceListSpider, MinuteSpider
from scraper.spiders.cityhall import BidsSpider
from scraper.spiders.gazette import (
    ExecutiveAndLegislativeGazetteSpider,
    LegacyGazetteSpider,
)
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings

from ._citycouncil import save_agenda, save_attendance_list, save_minute
from ._cityhall import save_bid
from ._gazette import save_gazette, save_legacy_gazette


class Command(BaseCommand):
    help = "Executa todos os coletores e salva os itens recentes no banco."

    def add_arguments(self, parser):
        drop_all_help = "Limpa o banco antes de iniciar a coleta."
        parser.add_argument("--drop-all", action="store_true", help=drop_all_help)

    def echo(self, text, style=None):
        self.stdout.write(style(text) if style else text)

    def warn(self, text):
        return self.echo(text, self.style.WARNING)

    def success(self, text):
        return self.echo(text, self.style.SUCCESS)

    def save(self, signal, sender, item, response, spider):
        if isinstance(item, CityCouncilAgendaItem):
            save_agenda(item)
        if isinstance(item, CityCouncilAttendanceListItem):
            save_attendance_list(item)
        if isinstance(item, CityCouncilMinuteItem):
            save_minute(item)
        if isinstance(item, CityHallBidItem):
            save_bid(item)
        if isinstance(item, LegacyGazetteItem):
            save_legacy_gazette(item)
        if isinstance(item, GazetteItem):
            save_gazette(item)

    def handle(self, *args, **options):
        if options.get("drop_all"):
            self.warn("Dropping existing records...")
            CityCouncilAgenda.objects.all().delete()
            CityCouncilAttendanceList.objects.all().delete()
            CityCouncilMinute.objects.all().delete()
            CityHallBid.objects.all().delete()
            Gazette.objects.all().delete()
            GazetteEvent.objects.all().delete()

        dispatcher.connect(self.save, signal=signals.item_passed)
        os.environ["SCRAPY_SETTINGS_MODULE"] = "scraper.settings"
        process = CrawlerProcess(settings=get_project_settings())
        process.crawl(
            AgendaSpider, start_from_date=CityCouncilAgenda.last_collected_item_date(),
        )
        process.crawl(
            AttendanceListSpider,
            start_from_date=CityCouncilAttendanceList.last_collected_item_date(),
        )
        process.crawl(
            MinuteSpider, start_from_date=CityCouncilMinute.last_collected_item_date()
        )
        process.crawl(
            BidsSpider, start_from_date=CityHallBid.last_collected_item_date()
        )

        last_collected_gazette = Gazette.last_collected_item_date()
        if last_collected_gazette is None:
            process.crawl(LegacyGazetteSpider)
        process.crawl(
            ExecutiveAndLegislativeGazetteSpider,
            start_from_date=last_collected_gazette,
        )

        process.start()
        self.success("Done!")
