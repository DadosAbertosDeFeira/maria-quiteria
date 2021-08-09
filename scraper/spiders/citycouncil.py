from datetime import date, datetime

import scrapy
from scraper.items import (
    CityCouncilAgendaItem,
    CityCouncilAttendanceListItem,
    CityCouncilMinuteItem,
)
from web.datasets.parsers import from_str_to_date

from . import BaseSpider
from .utils import datetime_utcnow_aware, months_and_years, strip_accents


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
    initial_date = date(2021, 4, 20)
    start_urls = ["https://www.feiradesantana.ba.leg.br/listadepresenca.asp"]

    @staticmethod
    def get_status(status):
        """Retorna label dos status. Consultado em 06/08/2021."""
        if not status:
            return ""
        status = strip_accents(status.strip())
        return status.lower().replace(" ", "_")

    def parse(self, response):
        boxes = response.css("div.row div div")
        current_page = response.meta.get("current_page", 1)
        last_page = response.css("ul.pagination li:last-child ::text").get()
        found = False

        for box in boxes:
            list_date = box.css("ul li ::text").get()
            if list_date:
                date_obj = datetime.strptime(list_date, "%d/%m/%Y")
                print(date_obj.date(), self.start_date)
                if date_obj.date() >= self.start_date:
                    found = True
                    list_url = box.css("div a::attr(href)").get()
                    yield scrapy.Request(
                        url=response.urljoin(list_url),
                        callback=self.parse_list_page,
                        meta={"date": list_date},
                    )

        if found and last_page:  # deve continuar checando até não encontrar mais
            last_page = int(last_page)
            next_page = current_page + 1
            if next_page <= last_page:
                yield scrapy.Request(
                    url=response.urljoin(f"listadepresenca.asp?p={next_page}"),
                    callback=self.parse,
                    meta={"current_page": next_page},
                )

    def parse_list_page(self, response):
        council_members = response.css("div.row div div ul li a::text").extract()
        status = response.css("div.row div div div a::text").extract()

        for council_member, status in zip(council_members, status):
            yield CityCouncilAttendanceListItem(
                crawled_at=datetime_utcnow_aware(),
                crawled_from=response.url,
                date=from_str_to_date(response.meta["date"]),
                council_member=council_member.strip(),
                status=self.get_status(status),
            )


class MinuteSpider(BaseSpider):
    name = "citycouncil_minutes"
    base_url = "https://www.feiradesantana.ba.leg.br"
    initial_date = date(2015, 1, 1)
    pages_by_type = {
        "sessao_ordinaria": "atas.asp?ida=1&nma=Sessão Ordinária",
        "sessao_solene": "atas.asp?ida=2&nma=Sessão Solene",
        "sessao_especial": "atas.asp?ida=3&nma=Sessões Especiais",
        "audiencia_publica": "atas.asp?ida=4&nma=Audiência Pública",
        "sessao_extraordinaria": "atas.asp?ida=5&nma=Sessão Extraordinária",
        "termo_de_encerramento": "atas.asp?ida=6&nma=Termo de Encerramento",
    }

    def start_requests(self):
        self.logger.info(f"Data inicial: {self.start_date}")
        today = datetime_utcnow_aware().date()

        for month, year in months_and_years(self.start_date, today):
            for event_type, type_url in self.pages_by_type.items():
                # formato esperado 2021-07-01
                next_month = month + 1 if month < 12 else 1
                next_month_year = year + 1 if month == 12 else year

                from_date = str(date(year, month, 1))
                to_date = str(date(next_month_year, next_month, 1))
                url = f"{self.base_url}/{type_url}&txtbus={from_date}&txtbus1={to_date}"

                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    meta={"event_type": event_type, "url_without_page": url},
                )

    def parse(self, response):
        dates = response.css("section div.row div div h3 ::text").getall()
        dates = [date_txt.replace("Data: ", "") for date_txt in dates]
        event_titles = response.css("section div.row div div ul li ::text").getall()
        file_urls = response.css("section div.row div div a::attr(href)").extract()
        file_urls = [f"https://www.feiradesantana.ba.leg.br/{url}" for url in file_urls]

        for event_date, title, file_url in zip(dates, event_titles, file_urls):
            event_date = from_str_to_date(event_date)
            yield CityCouncilMinuteItem(
                crawled_at=datetime_utcnow_aware(),
                crawled_from=response.url,
                date=event_date,
                title=title.strip(),
                event_type=response.meta["event_type"],
                files=[response.urljoin(file_url)],
            )

        pagination = response.css("section div ul.pagination li a")
        if pagination:
            current_page = response.css(
                "section div ul.pagination li.active ::text"
            ).get()
            if not current_page:
                current_page = response.css(
                    "section div ul.pagination li.current ::text"
                ).get()
            if current_page:
                next_page = int(current_page) + 1
                url = f"{response.meta['url_without_page']}&p={next_page}"
                yield scrapy.Request(url, callback=self.parse, meta=response.meta)
