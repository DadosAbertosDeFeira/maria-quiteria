import re
from datetime import date, datetime, timedelta

import scrapy
from scraper.items import CityHallBidItem, CityHallContractItem, CityHallPaymentsItem

from . import BaseSpider
from .utils import extract_param, identify_contract_id


class BidsSpider(BaseSpider):
    name = "cityhall_bids"
    start_urls = ["http://www.feiradesantana.ba.gov.br/seadm/licitacoes.asp"]
    initial_date = date(2001, 1, 1)

    def follow_this_date(self, url):
        month_year = extract_param(url, "dt")
        month_year = datetime.strptime(month_year, "%m-%Y")

        match_month = month_year.month >= self.start_date.month
        match_year = month_year.year >= self.start_date.year
        return match_month and match_year

    def parse(self, response):
        urls = response.xpath("//table/tbody/tr/td[1]/div/a//@href").extract()
        base_url = "http://www.feiradesantana.ba.gov.br"
        self.logger.info(f"Data inicial: {self.start_date}")

        for url in urls:
            if base_url not in url:
                # todos os anos exceto 2017 e 2018
                if url.startswith("servicos.asp"):
                    url = response.urljoin(f"{base_url}/{url}")
                else:
                    url = response.urljoin(f"{base_url}/seadm/{url}")

            if self.follow_this_date(url):
                yield response.follow(url, self.parse_page)

    def parse_page(self, response):
        raw_modalities = response.xpath("//tr/td[1]/table/tr/td/text()").extract()
        raw_descriptions = response.xpath(
            "//table/tr[2]/td/table/tr[6]/td/table/tr/td[2]/table[1]"
        )
        raw_bids_history = response.xpath(
            "//table/tr[2]/td/table/tr[6]/td/table/tr/td[2]/table[2]"
        )
        raw_date = response.xpath("//tr/td[3]/table/tr/td/text()").extract()
        descriptions = self._parse_descriptions(raw_descriptions)
        bids_history = self._parse_bids_history(raw_bids_history)
        modalities = self._parse_modalities(raw_modalities)
        date = self._parse_date(raw_date)
        bid_data = zip(modalities, descriptions, bids_history, date)

        url_pattern = re.compile(r"licitacoes_pm\.asp[\?|&]cat=(\w+)\&dt=(\d+-\d+)")
        for modality, (description, document_url), history, date in bid_data:
            match = url_pattern.search(response.url)
            month, year = match.group(2).split("-")

            item = CityHallBidItem(
                crawled_at=datetime.now(),
                crawled_from=response.url,
                category=match.group(1).upper(),
                month=int(month),
                year=int(year),
                description=description,
                history=history,
                modality=modality,
                date=date,
            )
            if document_url:
                item["file_urls"] = [response.urljoin(document_url)]
            yield item

    def _parse_descriptions(self, raw_descriptions):
        descriptions = []
        for raw_description in raw_descriptions:
            description = raw_description.xpath(".//text()").extract()
            document_url = raw_description.xpath(".//@href").extract_first()
            description = self._parse_description(description)

            if description != "Objeto":
                document_url = document_url if document_url else ""
                descriptions.append((description, document_url))
        return descriptions

    def _parse_bids_history(self, raw_bids_history):
        all_bids_history = []
        for raw_bid_history in raw_bids_history:
            bids_history = []
            for row in raw_bid_history.xpath(".//tr"):
                date = row.xpath(".//td[2]/text()").get().strip()
                event = row.xpath(".//td[3]/div/text()").get()
                url = row.xpath(".//td[4]/div/a//@href").get()

                if event and date:
                    url = url if url else ""
                    bids_history.append(
                        {"date": date, "event": event.capitalize(), "url": url}
                    )
            all_bids_history.append(bids_history)

        return all_bids_history

    def _parse_description(self, raw_descriptions):
        descriptions = []
        for raw_description in raw_descriptions:
            description = raw_description.strip()
            if not description.isspace():
                descriptions.append(description)
        return "".join(descriptions)

    def _parse_modalities(self, raw_modalities):
        modalities = []
        for raw_modality in raw_modalities:
            modality = raw_modality.strip()
            if modality != "":
                modality = modality.replace("\r\n", " / ")
                modalities.append(modality)
        return modalities

    def _parse_date(self, raw_date):
        return [date[1:] for date in raw_date]


class ContractsSpider(BaseSpider):
    """Coleta contratos da página de contratos.

    http://www.transparencia.feiradesantana.ba.gov.br/index.php?view=contratos
    """

    name = "cityhall_contracts"
    url = "http://www.transparencia.feiradesantana.ba.gov.br/controller/contrato.php"
    data = {
        "POST_PARAMETRO": "PesquisaContratos",
        "POST_DATA": "",
        "POST_NMCREDOR": "",
        "POST_CPFCNPJ": "",
        "POST_NUCONTRATO": "",
    }
    initial_date = date(2010, 1, 1)

    def start_requests(self):
        start_date = self.start_date
        self.logger.info(f"Data inicial: {start_date}")
        today = datetime.now().date()

        while start_date < today:
            formatted_date = start_date.strftime("%d/%m/%Y")
            data = self.data.copy()
            data["POST_DATA"] = f"{formatted_date} - {formatted_date}"
            yield scrapy.FormRequest(
                self.url, formdata=data, callback=self.parse, meta={"data": data}
            )
            start_date = start_date + timedelta(days=1)

    def parse(self, response):
        # ['��� Anterior', '1', '2', '33', 'Pr��ximo ���']
        pages = response.css("div.pagination li a ::text").extract()
        if pages:
            last_page = int(pages[-2])

            for page in range(1, last_page + 1):
                data = response.meta["data"]
                data["POST_PAGINA"] = str(page)
                data["POST_PAGINAS"] = str(last_page)
                yield scrapy.FormRequest(
                    self.url, formdata=data, callback=self.parse_page
                )

    def parse_page(self, response):
        """Extrai informações sobre um contrato.

        Example:
        CONTRATO N° 11-2017-1926C   REFERENTE A CONTRATAÇÃO DE EMPRESA AQUISIÇÃO DE
        ÁGUA MINERAL NATURAL PARA A...
        OBJETO:REFERENTE A CONTRATAÇÃO DE EMPRESA AQUISIÇÃO DE ÁGUA MINERAL NATURAL
        PARA ATENDER AS NECESSIDADES DA SUPERINTENDÊNCIA MUNICIPAL DE TRÂNSITO.
        CONTRATADA: 74.096.231/0001-80 - WAMBERTO LOPES DE ARAUJO - ME
        VALOR: R$ 62.960,00
        DATA FINAL DE CONTRATO: 01/06/2018
        """

        headlines = response.css('tbody tr:not([class^="informacao"])')
        contract_details = response.css("tr.informacao")
        base_url = "http://www.transparencia.feiradesantana.ba.gov.br"

        for headline, raw_details in zip(headlines, contract_details):
            contract_and_date = headline.css("th ::text").extract()
            contract_id = identify_contract_id(contract_and_date[0])
            starts_at = contract_and_date[1]
            details = self.clean_details(raw_details)
            document_url = raw_details.css("a.btn::attr(href)").get(default=None)

            contractor = details[1].split(" - ")
            contractor_document = contractor[0]
            contractor_name = contractor[1]

            item = CityHallContractItem(
                contract_id=contract_id,
                starts_at=starts_at,
                summary=details[0],
                contractor_document=contractor_document,
                contractor_name=contractor_name,
                value=details[2],
                ends_at=details[3],
                crawled_at=datetime.now(),
                crawled_from=response.url,
            )
            if document_url:
                item["file_urls"] = [f"{base_url}{document_url}"]
            yield item

    def clean_details(self, raw_details):
        labels = [
            "Objeto:",
            "Contratada:",
            "Valor:",
            "Data Final de Contrato:",
            "VISUALIZAR",
        ]

        valid_details = []
        for details in raw_details.css("p ::text").extract():
            details = details.strip()
            if details != "" and details not in labels:
                # assuming that all fields will be there
                valid_details.append(details)
        return valid_details


class PaymentsSpider(BaseSpider):
    """Coleta pagamentos realizados.

    http://www.transparencia.feiradesantana.ba.gov.br/index.php?view=despesa
    """

    name = "cityhall_payments"
    url = "http://www.transparencia.feiradesantana.ba.gov.br/controller/despesa.php"
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
        start_date = self.start_date
        self.logger.info(f"Data inicial: {start_date}")
        today = datetime.now().date()

        while start_date < today:
            formatted_date = start_date.strftime("%d/%m/%Y")
            data = self.data.copy()
            data["POST_DATA"] = f"{formatted_date} - {formatted_date}"
            yield scrapy.FormRequest(
                self.url, formdata=data, callback=self.parse, meta={"data": data}
            )
            start_date = start_date + timedelta(days=1)

    def parse(self, response):
        # ['��� Anterior', '1', '2', '33', 'Pr��ximo ���']
        pages = response.css("div.pagination li a ::text").extract()
        if pages:
            last_page = int(pages[-2])

            for page in range(1, last_page + 1):
                data = response.meta["data"]
                data["POST_PAGINA"] = str(page)
                data["POST_PAGINAS"] = str(last_page)
                yield scrapy.FormRequest(
                    self.url, formdata=data, callback=self.parse_page
                )

    def parse_page(self, response):
        """Extrai informações sobre um pagamento.

        Exemplo:
        N°: 19000215/0004 	CPF/CNPJ: 90.180.605/0001-02 	\
            Data: 22/10/2019 		N° do processo: 010-2019
        Bem / Serviço Prestado: REFERENTE A DESPESA COM SEGURO DE VIDA.
        Natureza: 339039999400 - Seguros em Geral
        Ação: 2015 - Manutencao dos serv.tecnicos administrativos
        Função: 04 - ADMINISTRACAO
        Subfunção: 122 - ADMINISTRACAO GERAL
        Processo Licitatório: PREGAO
        Fonte de Recurso: 0000 - RECURSOS ORDINARIOS
        """
        headlines = response.css("#editable-sample tr.accordion-toggle")
        details = response.css("#editable-sample div.accordion-inner")

        for headline, raw_details in zip(headlines, details):
            headline = [text.strip() for text in headline.css("td ::text").extract()]
            item = CityHallPaymentsItem(
                published_at=headline[0],
                phase=headline[1],
                company_or_person=headline[2],
                value=headline[3],
                crawled_at=datetime.now(),
                crawled_from=response.url,
            )
            details = [
                detail.strip() for detail in raw_details.css("td ::text").extract()
            ]
            mapping = {
                "N°:": "number",
                "CPF/CNPJ:": "document",
                "Data:": "date",
                "N° do processo:": "process_number",
                "Bem / Serviço Prestado:": "summary",
                "Natureza:": "group",
                "Ação:": "action",
                "Função:": "function",
                "Subfunção:": "subfunction",
                "Processo Licitatório:": "type_of_process",
                "Fonte de Recurso:": "resource",
            }
            details_copy = details.copy()
            while details_copy:
                key = details_copy.pop(0)
                value = details_copy.pop(0)
                item[mapping[key]] = value

            yield item
