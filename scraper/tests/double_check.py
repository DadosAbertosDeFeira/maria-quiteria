"""Compara relatórios do portal da transparência com dados crawleados.

Exemplo:
    python double_check.py contracts Relatorio-Contratos.xls contracts.json
"""
import argparse
import json

import pandas as pd  # FIXME add as dev-req


def match(mapping, key, report, crawled_data):
    from_report = pd.read_excel(report)  # FIXME adapt by file extension
    from_crawler = json.load(open(crawled_data))
    header = list(from_report.columns.values)

    if [*mapping] == header:
        for row_index, row in from_report.iterrows():
            found = False
            for crawled in from_crawler:
                if str(row[key]).strip() in crawled[mapping.get(key)].strip():
                    found = True
                    break
            if found is False:
                print(f"A linha {row_index+2} não foi encontrada ({row[key]}).")

    else:
        print("Existem colunas não mapeadas.")


def get_mapping(spider):
    schemas = json.load(open("report_schemas.json"))
    for schema in schemas:
        if schema["name"] == spider:
            return schema["id"], schema["mapping"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("spider", help="Nome do spider ou esquema de dados.")
    parser.add_argument("report", help="Relatório do Portal da Transparência.")
    parser.add_argument("crawled_data", help="Output dos dados crawleados.")
    args = parser.parse_args()

    key, mapping = get_mapping(args.spider)
    if mapping:
        match(mapping, key, args.report, args.crawled_data)
    else:
        print("Mapping not found.")
