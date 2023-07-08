from datetime import date

import scrapy
from scraper.items import (
    CityCouncilAgendaItem,
    CityCouncilAttendanceListItem,
    CityCouncilMinuteItem,
)
from web.datasets.parsers import from_str_to_date

from . import BaseSpider
from .utils import datetime_utcnow_aware, get_status, months_and_years


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
    initial_date = date(2022, 1, 1)
    start_urls = ["https://www.feiradesantana.ba.leg.br/lista-presenca"]
    events = {
        "Sessão Ordinária": "1",
        "Sessão Solene": "2",
        "Sessões Especiais": "3",
        "Audiência Pública": "4",
        "Sessão Extraordinária": "5",
        "Termo de Encerramento": "6",
    }

    def start_requests(self):
        for month, year in months_and_years(self.initial_date, date.today()):
            month = str(f"0{month}" if month < 10 else month)
            year = str(year)
            for event, event_number in self.events.items():
                url = (
                    f"https://www.feiradesantana.ba.leg.br/lista-presenca?"
                    f"mes={month}&"
                    f"ano={year}&"
                    f"Acessar=OK#{event_number}"
                )
                data = {"mes": month, "ano": year, "Acessar": "OK"}

                yield scrapy.FormRequest(
                    url,
                    formdata=data,
                    callback=self.parse_list_page,
                    meta={"event": event},
                )


    def parse_list_page(self, response):
        dates = response.css("div#myTabContent2 h4::text").extract()
        dates = self.remove_invalid_dates(dates)

        tables = response.css("table.table")

        for a_date in dates:
            table = tables.pop()
            info = table.css("div.TITULO::text").extract()
            council_members = []
            status = []
            index = 0
            while index < len(info):
                if index % 2 == 0:  # even
                    council_members.append(info[index])
                else:
                    status.append(info[index])
                index += 1

            for council_member, status in zip(council_members, status):
                yield CityCouncilAttendanceListItem(
                    crawled_at=datetime_utcnow_aware(),
                    crawled_from=response.url,
                    date=from_str_to_date(a_date),
                    council_member=council_member.strip(),
                    status=get_status(status),
                    description=response.meta["event"],
                )

    @staticmethod
    def remove_invalid_dates(dates):
        for c_date in range(0, len(dates)):
            if c_date >= len(dates): break

            if '      ' in dates[c_date]:
                dates.pop(c_date)

        return dates


class MinuteSpider(BaseSpider):
    name = "citycouncil_minutes"
    initial_date = date(2022, 1, 1)
    base_url = "https://www.feiradesantana.ba.leg.br/atas"
    events = {
        "Sessão Ordinária": "1",
        "Sessão Solene": "2",
        "Sessões Especiais": "3",
        "Audiência Pública": "4",
        "Sessão Extraordinária": "5",
        "Termo de Encerramento": "6",
    }

    def start_requests(self):
        for month, year in months_and_years(self.initial_date, date.today()):
            month = str(f"0{month}" if month < 10 else month)
            year = str(year)
            for event, event_number in self.events.items():
                url = (
                    f"https://www.feiradesantana.ba.leg.br/atas?"
                    f"mes={month}&"
                    f"ano={year}&"
                    f"Acessar=OK#{event_number}"
                )
                data = {"mes": month, "ano": year, "Acessar": "OK"}

                yield scrapy.FormRequest(
                    url, formdata=data, callback=self.parse, meta={"event": event}
                )


    def parse(self, response):
        dates = response.xpath("//table/tbody/tr/td[1]/strong/text()").getall()
        event_titles = response.xpath("//table/tbody/tr/td[2]/p/strong/text()").getall()
        file_urls = response.xpath("//table/tbody/tr/td[2]/p/a/@href").getall()
        file_urls = [f"https://www.feiradesantana.ba.leg.br/{url}" for url in file_urls]

        for event_date, title, file_url in zip(dates, event_titles, file_urls):
            event_date = from_str_to_date(event_date)
            yield CityCouncilMinuteItem(
                crawled_at=datetime_utcnow_aware(),
                crawled_from=response.url,
                date=event_date,
                title=title.strip(),
                event_type=response.meta["event"],
                files=[response.urljoin(file_url)],
            )
