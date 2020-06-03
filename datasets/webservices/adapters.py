from datasets.models import CityCouncilBid, CityCouncilContract, CityCouncilExpense
from datasets.parsers import (
    currency_to_float,
    from_str_to_date,
    from_str_to_datetime,
    get_phase,
    lower,
    modality_mapping_from_city_council_db,
    to_boolean,
)

CITYCOUNCIL_BID_FIELDS_MAPPING = {
    "CODLIC": "external_code",
    "CODTIPOLIC": "modality",
    "NUMLIC": "code",
    "NUMTIPOLIC": "code_type",
    "OBJETOLIC": "description",
    "DTLIC": "session_at",
    "EXCLUIDO": "excluded",
}


CITYCOUNCIL_BID_FUNCTIONS = {
    "excluded": to_boolean,
    "session_at": from_str_to_datetime,
    "modality": modality_mapping_from_city_council_db,
}


CITYCOUNCIL_CONTRACT_FIELDS_MAPPING = {
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

CITYCOUNCIL_CONTRACT_FUNCTIONS = {
    "value": currency_to_float,
    "excluded": to_boolean,
    "start_date": from_str_to_date,
    "end_date": from_str_to_date,
}


def map_to_fields(item, fields_mapping, functions):
    new_item = {}
    for key, value in item.items():
        field = fields_mapping[key.upper()]
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
    new_item = map_to_fields(
        item, CITYCOUNCIL_CONTRACT_FIELDS_MAPPING, CITYCOUNCIL_CONTRACT_FUNCTIONS
    )
    return CityCouncilContract(**new_item)


def to_bid(item):
    new_item = map_to_fields(
        item, CITYCOUNCIL_BID_FIELDS_MAPPING, CITYCOUNCIL_BID_FUNCTIONS
    )
    return CityCouncilBid(**new_item)
