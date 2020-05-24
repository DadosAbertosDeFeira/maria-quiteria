from datasets.models import (
    CityCouncilBid,
    CityCouncilContract,
    CityCouncilExpense,
    CityCouncilRevenue,
)
from datasets.parsers import (
    city_council_revenue_type_mapping,
    currency_to_float,
    from_str_to_date,
    from_str_to_datetime,
    get_phase,
    lower,
    modality_mapping_from_city_council_db,
    to_boolean,
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
        "CODTIPOLIC": "modality",
        "NUMLIC": "code",
        "NUMTIPOLIC": "code_type",
        "OBJETOLIC": "description",
        "DTLIC": "session_at",
        "EXCLUIDO": "excluded",
    }
    functions = {
        "excluded": to_boolean,
        "session_at": from_str_to_datetime,
        "modality": modality_mapping_from_city_council_db,
    }
    new_item = map_to_fields(item, fields_mapping, functions)
    return CityCouncilBid(**new_item)


def to_revenue(item):
    fields_mapping = {
        "CODLINHA": "external_code",
        "CODUNIDGESTORA": "budget_unit",
        "DTPUBLICACAO": "published_at",
        "DTREGISTRO": "registered_at",
        "TIPOREC": "revenue_type",
        "MODALIDADE": "modality",
        "DSRECEITA": "description",
        "VALOR": "value",
        "FONTE": "resource",
        "DSNATUREZA": "legal_status",
        "DESTINACAO": "destination",
        "EXCLUIDO": "excluded",
    }
    functions = {
        "excluded": to_boolean,
        "published_at": from_str_to_date,
        "registered_at": from_str_to_date,
        "value": currency_to_float,
        "modality": lower,
        "revenue_type": city_council_revenue_type_mapping,
        "resource": lower,
        "legal_status": lower,
        "destination": lower,
    }
    new_item = map_to_fields(item, fields_mapping, functions)
    return CityCouncilRevenue(**new_item)
