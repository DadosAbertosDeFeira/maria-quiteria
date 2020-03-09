from datetime import date, datetime

import scrapy
from scraper.items import EmployeesItem

from . import BaseSpider


class EmployeesSpider(BaseSpider):
    """Coleta dos pagamentos feitos a servidores municipais.

    Fonte: Tribunal de Contas do Município
    https://www.tcm.ba.gov.br/portal-da-cidadania/pessoal/

    Entidades foram consultadas em 01/03/2020
    """

    name = "municipalauditcourt_employees"
    url = "https://webservice.tcm.ba.gov.br/exportar/pessoal"
    data = {
        "tipo": "pdf",
        "entidades": "",
        "ano": "",  # formato AAAA
        "mes": "",  # formato M
        "cpf": "",
        "tipoRegime": "",
    }
    entities = {
        "129": "Prefeitura Municipal de FEIRA DE SANTANA",
        "544": "Camara Municipal de FEIRA DE SANTANA",
        "880": "Instituto de Previdência de Feira de Santana",
        "892": "Fundação Hospitalar de Feira de Santana",
        "984": "Superintendência Municipal de Trânsito",
        "1008": "Fundação Cultural Municipal Egberto Tavares Costa",
        "1032": "Superintendência Municipal de Proteção e Defesa do Consumidor",
        "1033": "Agência Reguladora de Feira de Santana",
        "1104": "Consórcio Público Interfederativo De "
        + "Saúde Da Região de Feira de Santana",
    }
    initial_date = date(2000, 1, 1)
    handle_httpstatus_list = [302]

    def start_requests(self):
        start_date = self.start_date
        self.logger.info(f"Data inicial: {start_date}")

        if start_date == self.initial_date:  # coleta desde o início
            today = datetime.now().date()
            for year in range(start_date.year, today.year + 1):
                for month in range(start_date.month, 13):
                    for entitity_id, entitity_name in self.entities.items():
                        data = self.data.copy()
                        data["entidades"] = entitity_id
                        data["ano"] = str(year)
                        data["mes"] = str(month)
                        meta = {"data": data, "agency": entitity_name}
                        yield scrapy.FormRequest(
                            self.url, formdata=data, callback=self.parse, meta=meta
                        )
        else:
            month = start_date.month
            year = start_date.year
            for entitity_id, entitity_name in self.entities.items():
                data = self.data.copy()
                data["entidades"] = entitity_id
                data["ano"] = str(year)
                data["mes"] = str(month)
                meta = {"data": data, "agency": entitity_name}
                yield scrapy.FormRequest(
                    self.url, formdata=data, callback=self.parse, meta=meta
                )

    def parse(self, response):
        paychecks = response.xpath("//tr")

        for paycheck in paychecks:
            num_of_columns_paychecks = 10
            if len(paycheck.css("td")) == num_of_columns_paychecks:
                columns = paycheck.css("td")
                fields = [
                    "nome",
                    "matricula",
                    "tipo_servidor",
                    "cargo",
                    "salario_base",
                    "salario_vantagens",
                    "salario_gratificacao",
                    "carga_horaria",
                    "situacao",
                    "ingresso_ou_admissao",
                ]

                extracted_data = {
                    "orgao": response.request.meta["agency"],
                    "mes": response.request.meta["data"]["mes"],
                    "ano": response.request.meta["data"]["ano"],
                }

                for field, column in zip(fields, columns):
                    extracted_data[field] = column.css("::text").extract_first()

                yield EmployeesItem(
                    crawled_at=datetime.now(),
                    crawled_from=response.url,
                    agency=extracted_data["orgao"],
                    month=extracted_data["mes"],
                    year=extracted_data["ano"],
                    name=extracted_data["nome"],
                    registration_number=extracted_data["matricula"],
                    condition=extracted_data["tipo_servidor"],
                    role=extracted_data["cargo"],
                    base_salary=extracted_data["salario_base"],
                    benefits_salary=extracted_data["salario_vantagens"],
                    bonus_salary=extracted_data["salario_gratificacao"],
                    workload=extracted_data["carga_horaria"],
                    status=extracted_data["situacao"],
                    admission=extracted_data["ingresso_ou_admissao"],
                )
