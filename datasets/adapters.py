from datasets.models import CityCouncilExpense
from datasets.parsers import (
    currency_to_float,
    from_str_to_date,
    get_phase,
    lower,
    to_boolean,
)


def to_expense(item):
    citycouncil_expenses = {
        "CODARQUIVO": None,
        "CODLINHA": None,
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
    new_item = {}
    for key, value in item.items():
        field = citycouncil_expenses[key]
        if field:
            value = value.strip()
            new_item[field] = functions.get(field, lambda x: x)(value)
    return CityCouncilExpense(**new_item)
