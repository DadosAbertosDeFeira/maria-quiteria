from datasets.models import CityCouncilAgenda, Employee
from django.core.management.base import BaseCommand
from scraper.items import CityCouncilAgendaItem, EmployeeItem
from scraper.spiders.citycouncil import AgendaSpider
from scraper.spiders.municipalauditcourt import EmployeesSpider
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher


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
            CityCouncilAgenda.objects.update_or_create(
                crawled_at=item["crawled_at"],
                crawled_from=item["crawled_from"],  # FIXME defaults?
                date=item["date"],
                details=item["details"],
                title=item["title"],
                event_type=item["event_type"],
            )

        if isinstance(item, EmployeeItem):
            Employee.objects.update_or_create(**item)

    def handle(self, *args, **options):
        if options.get("drop_all"):
            self.warn("Dropping existing records...")
            CityCouncilAgenda.objects.all().delete()
            Employee.objects.all().delete()

        dispatcher.connect(self.save, signal=signals.item_passed)
        process = CrawlerProcess()
        process.crawl(AgendaSpider)
        process.crawl(
            EmployeesSpider, start_from_date=Employee.last_collected_item_date()
        )
        process.start()
        self.success("Done!")
