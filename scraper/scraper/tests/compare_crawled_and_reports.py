"""This is a script to compared crawled data and reports from city hall website."""
import csv

import xlrd

mapping = {
    "Data de Publicacao": "published_at",
    "Fase ": "phase",
    "Numero": "number",
    "N do processo": "process_number",
    "Bem / Servico Prestado": "summary",
    "Credor": "company_or_person",
    "CPF / CNPJ": "document",
    "Valor": "value",
    "Funcao": "function",
    "Subfuncao": "subfunction",
    "Natureza": "group",
    "Fonte": "resource",
    "Modalidade": "type_of_process",
}

from_report = xlrd.open_workbook("Relatorio-Despesa-2010.xls")
from_crawler = csv.DictReader(open("pag-2010.csv"), delimiter=",", quotechar='"')

sheet = from_report.sheet_by_index(0)
header_from_report = sheet.row(0)

print(header_from_report)
print(from_crawler.fieldnames)
print("----------------")

for label in header_from_report:
    print(label.value, mapping.get(label.value))

# TODO check missing data
