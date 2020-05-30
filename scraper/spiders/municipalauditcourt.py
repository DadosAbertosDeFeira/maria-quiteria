from datetime import date, datetime

import scrapy
from datasets.parsers import currency_to_float, from_str_to_datetime
from scraper.items import EmployeeItem

from . import BaseSpider
from .utils import months_and_years


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

        today = datetime.now().date()
        for month, year in months_and_years(start_date, today):
            for entitity_id, entitity_name in self.entities.items():
                data = self.data.copy()
                data["entidades"] = entitity_id
                data["ano"] = str(start_date.year)
                data["mes"] = str(start_date.month)
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

                if extracted_data["ingresso_ou_admissao"]:
                    supported_formats = ["%d/%m/%Y", "%d/%m/%y"]
                    admission = from_str_to_datetime(
                        extracted_data["ingresso_ou_admissao"], supported_formats
                    ).date()
                else:
                    admission = extracted_data["ingresso_ou_admissao"]
                base_salary = currency_to_float(extracted_data["salario_base"])
                benefits_salary = currency_to_float(extracted_data["salario_vantagens"])
                bonus_salary = currency_to_float(extracted_data["salario_gratificacao"])

                yield EmployeeItem(
                    crawled_at=datetime.now(),
                    crawled_from=response.url,
                    agency=extracted_data["orgao"],
                    month=int(extracted_data["mes"]),
                    year=int(extracted_data["ano"]),
                    name=extracted_data["nome"],
                    registration_number=extracted_data["matricula"],
                    condition=extracted_data["tipo_servidor"],
                    role=extracted_data["cargo"],
                    base_salary=base_salary,
                    benefits_salary=benefits_salary,
                    bonus_salary=bonus_salary,
                    workload=int(extracted_data["carga_horaria"]),
                    status=extracted_data["situacao"],
                    admission=admission,
                )
