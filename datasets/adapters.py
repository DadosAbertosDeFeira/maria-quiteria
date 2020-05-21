from datasets.models import CityCouncilContract, CityCouncilExpense, CityCouncilBid
from datasets.parsers import (
    currency_to_float,
    from_str_to_date,
    get_phase,
    lower,
    to_boolean,
    from_str_to_datetime,
)


def map_to_fields(item, fields_mapping, functions):
    new_item = {}
    for key, value in item.items():
        field = fields_mapping[key]
        if field:
            value = value.strip()
            new_item[field] = functions.get(field, lambda x: x)(value)
    return new_item


def to_expense(item):
    fields_mapping = {
        "CODARQUIVO": "external_file_code",
        "CODLINHA": "external_file_line",
        "CODUNIDORCAM": "budget_unit",
        "DTPUBLICACAO": "published_at",
        "DTREGISTRO": "date",
        "CODETAPA": "phase",
        "NUMPROCADM": "number",
        "NUMPROCLIC": "process_number",
        "DSDESPESA": "summary",
        "NMCREDOR": "company_or_person",
        "NUCPFCNPJ": "document",
        "VALOR": "value",
        "DSFUNCAO": "function",
        "DSSUBFUNCAO": "subfunction",
        "DSNATUREZA": "legal_status",  # TODO natureza do TCM-BA
        "DSFONTEREC": "resource",
        "NUMETAPA": "phase_code",
        "MODALIDADE": "modality",
        "EXCLUIDO": "excluded",
    }
    functions = {
        "value": currency_to_float,
        "excluded": to_boolean,
        "published_at": from_str_to_date,
        "date": from_str_to_date,
        "phase": get_phase,
        "modality": lower,
    }
    new_item = map_to_fields(item, fields_mapping, functions)
    return CityCouncilExpense(**new_item)


def to_contract(item):
    fields_mapping = {
        "CODCON": "external_code",
        "DSCON": "description",
        "OBJETOCON": "details",
        "CPFCNPJCON": "company_or_person_document",
        "NMCON": "company_or_person",
        "VALORCON": "value",
        "DTCON": "start_date",
        "DTCONFIM": "end_date",
        "EXCLUIDO": "excluded",
    }
    functions = {
        "value": currency_to_float,
        "excluded": to_boolean,
        "start_date": from_str_to_date,
        "end_date": from_str_to_date,
    }
    new_item = map_to_fields(item, fields_mapping, functions)
    return CityCouncilContract(**new_item)


def to_bid(item):
    fields_mapping = {
        "CODLIC": "external_code",
        "CODTIPOLIC": "external_code_type",
        "NUMLIC": "code",
        "NUMTIPOLIC": "code_type",
        "OBJETOLIC": "description",
        "DTLIC": "session_at",
        "EXCLUIDO": "excluded",
    }
    functions = {
        "excluded": to_boolean,
        "session_at": from_str_to_datetime,
    }
    new_item = map_to_fields(item, fields_mapping, functions)
    return CityCouncilBid(**new_item)
