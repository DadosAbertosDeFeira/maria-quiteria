import json
import os
from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings
from tcmba.items import DocumentItem
from tcmba.spiders.consulta_publica import ConsultaPublicaSpider

from web.datasets.management.commands._tcmba import save_document


class Command(BaseCommand):
    """Raspa documentos de uma unidade no TCM-BA.

    Unidades:
        "Camara Municipal de FEIRA DE SANTANA"
        "Agência Reguladora de Feira de Santana - ARFES"
        "Fundação Hospitalar de Feira de Santana"
        "Superintendência Municipal de Proteção e Defesa do Consumidor"
        "Consórcio Público Interfederativo De Saúde Da Região de Feira de Santana"
        "Fundação Cultural Municipal Egberto Tavares Costa"
        "Superintendência Municipal de Trânsito - SMT"
        "Instituto de Previdência de Feira de Santana - IPFS"
    """

    help = "Executa raspador de documentos públicos do TCM-BA e salva no banco."

    def add_arguments(self, parser):
        parser.add_argument("--period")
        parser.add_argument("--period-type", default="mensal")
        parser.add_argument(
            "--unit", default="Prefeitura Municipal de FEIRA DE SANTANA"
        )
        parser.add_argument("--scrapy-args")

    def echo(self, text, style=None):
        self.stdout.write(style(text) if style else text)

    def warn(self, text):
        return self.echo(text, self.style.WARNING)

    def success(self, text):
        return self.echo(text, self.style.SUCCESS)

    def save(self, signal, sender, item, response, spider):
        if isinstance(item, DocumentItem):
            save_document(item)

    def handle(self, *args, **options):
        if not options.get("period"):
            target_date = date.today() + relativedelta(months=-2)
            target_date = target_date.strftime("%m/%Y")
        else:
            target_date = options.get("period")

        dispatcher.connect(self.save, signal=signals.item_passed)
        os.environ["SCRAPY_SETTINGS_MODULE"] = "scraper.settings"
        settings = get_project_settings()
        settings["COOKIES_ENABLED"] = True

        if options.get("scrapy_args"):
            scrapy_args = json.loads(options.get("scrapy_args"))
            settings.update(scrapy_args)

        process = CrawlerProcess(settings=settings)

        args = {
            "unidade": options.get("unit"),
            "competencia": target_date,
            "cidade": "feira de santana",
            "periodicidade": options.get("period_type"),
        }
        self.warn(str(args))
        process.crawl(ConsultaPublicaSpider, **args)
        self.warn("Iniciando a coleta dos documentos do TCM-BA...")
        process.start()
        self.success("Pronto!")
