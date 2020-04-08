import re
from datetime import date, datetime

import scrapy
from scraper.items import (
    CityCouncilAgendaItem,
    CityCouncilAttendanceListItem,
    CityCouncilMinuteItem,
)

from . import BaseSpider
from .utils import extract_date, from_str_to_date, months_and_years


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
                crawled_at=datetime.now(),
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
        today = datetime.now().date()
        if self.start_date != self.initial_date:
            # pega do início do ano corrente
            self.start_date = date(today.year, 1, 1)
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
                crawled_at=datetime.now(),
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
        today = datetime.now().date()

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
                crawled_at=datetime.now(),
                crawled_from=response.url,
                date=event_date,
                title=title.strip(),
                event_type=self.get_type(title),
                file_urls=[response.urljoin(file_url)],
            )


class ExpensesSpider(BaseSpider):
    name = "citycouncil_expenses"
    url = "https://www.transparencia.feiradesantana.ba.leg.br/controller/despesa.php"
    data = {
        "POST_PARAMETRO": "PesquisaDespesas",
        "POST_FASE": "",
        "POST_UNIDADE": "",
        "POST_DATA": "",
        "POST_NMCREDOR": "",
        "POST_CPFCNPJ": "",
    }
    initial_date = date(2010, 1, 1)

    def start_requests(self):
        data = self.data.copy()
        meta = {"dont_redirect": True, "handle_httpstatus_list": [302], "data": data}
        yield scrapy.FormRequest(
            self.url, formdata=data, callback=self.parse, meta=meta
        )

    def parse(self, response):
        # ['��� Anterior', '1', '2', '1705', 'Pr��ximo ���']
        pages = response.css("div.pagination li a ::text").extract()
        if pages:
            last_page = int(pages[-2])
            # TODO filtro por data

            for page in range(1, last_page + 1):
                data = response.meta["data"]
                data["POST_PAGINA"] = str(page)
                data["POST_PAGINAS"] = str(last_page)
                yield scrapy.FormRequest(
                    self.url,
                    formdata=data,
                    callback=self.parse_page,
                    meta=response.meta,
                )

    def parse_page(self, response):
        """Extrai informações sobre as despesas.

        Exemplo:
        N°: 01346/00
        CPF/CNPJ: 119.121.205-00
        Data: 21/10/2010
        N° do processo:
        Bem / Serviço Prestado: REF. A 2 E 1/2 DIARIAS P/ VEREADORA PARTICIPAR
            DO SEMINÁRIO CAPACITANDO VEREADORES DO BRASIL PARA UM NOVO MILÊNIO,
            EM SALVADOR-BA, DE 27 A 29/08/2010.
        Natureza: 339014000000 - Diarias-Civil 2001 -
            Administracao de pessoal e encargos
        Função: 01 - LEGISLATIVA
        Subfunção: 031 - ACAO
        Processo Licitatório: ISENTO
        Fonte de Recurso: 0000 - TESOURO
        """
        headlines = response.css("#editable-sample tr.accordion-toggle")
        details = response.css("#editable-sample div.accordion-inner")

        for headline, raw_details in zip(headlines, details):
            headline = [text.strip() for text in headline.css("td ::text").extract()]
            item = {
                "published_at": headline[0],
                "phase": headline[1],
                "company_or_person": headline[2],
                "value": headline[3],
                "crawled_at": datetime.now(),
                "crawled_from": response.url,
            }
            details = [
                detail.strip() for detail in raw_details.css("td ::text").extract()
            ]
            mapping = {
                "N°:": "number",
                "CPF/CNPJ:": "document",
                "Data:": "date",
                "N° do processo:": "process_number",
                "Bem / Serviço Prestado:": "summary",
                "Natureza:": "legal_status",
                "Ação:": "action",
                "Função:": "function",
                "Subfunção:": "subfunction",
                "Processo Licitatório:": "type_of_process",
                "Fonte de Recurso:": "resource",
            }
            details_copy = details.copy()
            while details_copy:
                key = details_copy.pop(0)
                if key == "imprimir":
                    break
                value = details_copy.pop(0)
                if key == "Natureza:":
                    subgroup_and_group = self.extract_subgroup_and_group(value)
                    if subgroup_and_group:
                        subgroup, group = subgroup_and_group
                        item["subgroup"] = subgroup
                        item["group"] = group
                item[mapping[key]] = value

            yield item

    @staticmethod
    def extract_subgroup_and_group(legal_status):
        result = re.match(r"\d+ - (.*) \d+ - (.*)", legal_status)
        if result:
            return result.group(1).strip(), result.group(2).strip()
