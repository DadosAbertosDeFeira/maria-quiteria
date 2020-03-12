from datetime import date, datetime

import scrapy
from scraper.items import CityCouncilAgendaItem
from scraper.spiders.utils import from_str_to_datetime

from . import BaseSpider


class AgendaSpider(BaseSpider):
    name = "citycouncil_agenda"
    start_urls = ["https://www.feiradesantana.ba.leg.br/agenda"]
    initial_date = date(2010, 1, 1)

    @staticmethod
    def get_type(event_title):
        if "ordem do dia" in event_title.lower():
            return "ordem_do_dia"
        if "sessão solene" in event_title.lower():
            return "sessao_solene"
        if "sessão especial" in event_title.lower():
            return "sessao_especial"
        if "audiência pública" in event_title.lower():
            return "audiencia_publica"
        return "not_found"

    def parse(self, response):
        self.logger.info(f"Data inicial: {self.start_date}")

        extracted_years = response.css("select#ano option ::text").extract()
        years = []
        for year in extracted_years:
            try:
                years.append(int(year))
            except ValueError:
                pass

        for year in range(min(years), max(years) + 1):
            if self.start_date.year <= year:
                for month in range(1, 13):
                    if self.start_date.month <= month:
                        url = (
                            "https://www.feiradesantana.ba.leg.br/agenda"
                            f"?mes={month}&ano={year}&Acessar=OK"
                        )
                        yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        event_details = response.css("div.feature-box")
        dates = response.xpath("//table/tbody/tr/td[1]/strong/text()").getall()
        event_titles = response.xpath("//table/tbody/tr/td[2]/p/strong/text()").getall()

        for details, event_date, title in zip(event_details, dates, event_titles):
            events = [
                line.strip()
                for line in details.css("p ::text").getall()
                if line.strip() != ""
            ]

            supported_formats = ["%d/%m/%Y", "%d/%m/%y"]
            event_date = from_str_to_datetime(event_date, supported_formats).date()

            yield CityCouncilAgendaItem(
                crawled_at=datetime.now(),
                crawled_from=response.url,
                date=event_date,
                details=" ".join(events),
                title=title.strip(),
                event_type=self.get_type(title),
            )
