from datetime import date

import scrapy
from web.datasets.parsers import from_str_to_date
from scraper.items import (
    CityCouncilAgendaItem,
    CityCouncilAttendanceListItem,
    CityCouncilMinuteItem,
)

from . import BaseSpider
from .utils import datetime_utcnow_aware, extract_date, months_and_years


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
            event_date = from_str_to_date(event_date)
            yield CityCouncilAgendaItem(
                crawled_at=datetime_utcnow_aware(),
                crawled_from=response.url,
                date=event_date,
                details=" ".join(events),
                title=title.strip(),
                event_type=self.get_type(title),
            )


class AttendanceListSpider(BaseSpider):
    name = "citycouncil_attendancelist"
    initial_date = date(2020, 1, 1)

    @staticmethod
    def get_status(status):
        """"Retorna label dos status. Consultado em 20/03/2020."""
        status_labels = {
            "P": "presente",
            "FJ": "falta_justificada",
            "LJ": "licenca_justificada",
            "A": "ausente",
        }

        return status_labels.get(status.upper().strip())

    def start_requests(self):
        today = datetime_utcnow_aware().date()
        self.logger.info(f"Data inicial: {self.start_date}")

        for month, year in months_and_years(self.start_date, today):
            url = (
                "https://www.feiradesantana.ba.leg.br/lista-presenca"
                f"?mes={month}&ano={year}&Acessar=OK"
            )
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        list_page = response.xpath("//p/a/@href").extract()

        for page in list_page:
            yield scrapy.Request(
                url=response.urljoin(page), callback=self.parse_list_page
            )

    def parse_list_page(self, response):
        title = response.css("div.center h3 ::text").extract_first()
        description = response.css("div.center p strong ::text").extract_first()
        council_members = response.xpath("//tr/td[1]/div/text()").extract()
        status = response.xpath("//tr/td[2]/div/text()").extract()

        for council_member, status in zip(council_members, status):
            yield CityCouncilAttendanceListItem(
                crawled_at=datetime_utcnow_aware(),
                crawled_from=response.url,
                date=extract_date(title),
                description=description.strip() if description else "",
                council_member=council_member,
                status=self.get_status(status),
            )


class MinuteSpider(BaseSpider):
    name = "citycouncil_minutes"
    start_urls = ["https://www.feiradesantana.ba.leg.br/atas"]
    initial_date = date(2015, 1, 1)

    @staticmethod
    def get_type(event_title):
        if "sessão ordinária" in event_title.lower():
            return "sessao_ordinaria"
        if "sessões ordinárias" in event_title.lower():
            return "sessao_ordinaria"
        if "ordem do dia" in event_title.lower():
            return "ordem_do_dia"
        if "sessão solene" in event_title.lower():
            return "sessao_solene"
        if "sessão especial" in event_title.lower():
            return "sessao_especial"
        if "audiência pública" in event_title.lower():
            return "audiencia_publica"
        return

    def start_requests(self):
        self.logger.info(f"Data inicial: {self.start_date}")
        today = datetime_utcnow_aware().date()

        for month, year in months_and_years(self.start_date, today):
            url = (
                "https://www.feiradesantana.ba.leg.br/atas"
                f"?mes={month}&ano={year}&Acessar=OK"
            )
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        dates = response.xpath("//table/tbody/tr/td[1]/strong/text()").getall()
        event_titles = response.xpath("//table/tbody/tr/td[2]/p/strong/text()").getall()
        file_urls = response.xpath("//p/a/@href").extract()

        for event_date, title, file_url in zip(dates, event_titles, file_urls):
            event_date = from_str_to_date(event_date)
            yield CityCouncilMinuteItem(
                crawled_at=datetime_utcnow_aware(),
                crawled_from=response.url,
                date=event_date,
                title=title.strip(),
                event_type=self.get_type(title),
                files=[response.urljoin(file_url)],
            )
