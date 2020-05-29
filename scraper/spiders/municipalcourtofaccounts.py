from datetime import date, datetime

import scrapy
from scraper.spiders import BaseSpider


class ConstructionSpider(BaseSpider):
    """Coleta obras do Tribunal de Contas dos Municípios.

    Fonte: https://www.tcm.ba.gov.br/portal-da-cidadania/obras/
    """

    name = "municipalcourtofaccounts_constructions"
    city_code = "2910800"  # Feira de Santana
    entities = {
        "129": "Prefeitura Municipal de FEIRA DE SANTANA",
        "544": "Camara Municipal de FEIRA DE SANTANA",
        "880": "Instituto de Previdência de Feira de Santana",
        "892": "Fundação Hospitalar de Feira de Santana",
        "984": "Superintendência Municipal de Trânsito",
        "1008": "Fundação Cultural Municipal Egberto Tavares Costa",
        "1032": "Superintendência Municipal de Proteção e Defesa do Consumidor",
        "1033": "Agência Reguladora de Feira de Santana",
        "1104": "Consórcio Público Interfederativo De Saúde "
        "Da Região de Feira de Santana",
    }

    def start_requests(self):
        current_year = date.today().year
        for year in range(2000, current_year + 1):
            for code, entity in self.entities.items():
                url = (
                    f"https://www.tcm.ba.gov.br/portal-da-cidadania/obras/"
                    f"?municipio={self.city_code}&entidade={code}&ano={year}"
                    f"&dsObra=&dtlObra=&empresaObra=&stObra=&pesquisar=Pesquisar"
                    f"&pesquisar=Pesquisar"
                )
                yield scrapy.Request(
                    url=url, callback=self.parse, meta={"entity": entity}
                )

    def parse(self, response):
        for row in response.css("table#tabelaResultado tr"):
            columns = row.css("td")
            if columns:
                construction = {
                    "entity": response.meta["entity"],
                    "crawled_from": response.url,
                    "crawled_at": datetime.now(),
                }
                column_labels = [
                    "code",
                    "description",
                    "status",
                    "type",
                    "cost",
                    "paid_value",
                    "retained_value",
                    "company",
                    "details_url",
                ]
                for column in columns:
                    label = column_labels.pop(0)
                    text = column.css("::text").extract_first()
                    if text:
                        text = text.strip()
                    construction[label] = text

                # padrão: "window.location = 'https://"
                details_page = (
                    row.css("td")[-1].css("button::attr(onclick)").extract_first()
                )
                url_start = "window.location = '"
                if details_page:
                    yield response.follow(
                        details_page[len(url_start):-1],
                        self.parse_details_page,
                        meta={"construction": construction},
                    )

    def parse_details_page(self, response):
        construction = response.meta["construction"]
        construction["details_page"] = response.url

        details_label = response.css("div.form-group label ::text").extract()
        details_value = response.css(
            "div.form-group:not(.subtitle) span ::text"
        ).extract()
        construction["details"] = {}
        for label, value in zip(details_label, details_value):
            construction["details"][label] = value
        construction["additives"] = []
        construction["payments"] = []
        tables = response.css("table.table.table-striped")
        if tables:
            additive_table = response.xpath(
                "//h4[text()='Dados do Aditivo']/following::table"
            )
            payments_table = response.xpath(
                "//h4[text()='Dados dos Pagamentos']/following::table"
            )
            construction["additives"] = self.get_additives(additive_table)
            construction["payments"] = self.get_payments(payments_table)
        yield construction

    def get_additives(self, table):
        labels = [
            "additive_number",
            "register_date",
            "start_date",
            "term_in_days",  # prazo
            "value",
            "quarter",  # semestre
        ]
        return self.from_table_to_dict(table, labels)

    def get_payments(self, table):
        labels = [
            "date",
            "to_be_paid_document",  # empenho
            "process_number",
            "paid_value",
            "quarter",  # semestre
        ]
        return self.from_table_to_dict(table, labels)

    @staticmethod
    def from_table_to_dict(table, labels):
        result = []
        if not table:
            return
        for row in table.css("tr"):
            columns = row.css("td")
            data = {}
            for index, column in enumerate(columns):
                text = column.css("::text").extract_first()
                if text:
                    text = text.strip()
                data[labels[index]] = text
            if data:
                result.append(data)
        return result
