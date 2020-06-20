import logging

from datasets.models import (
    CityCouncilBid,
    CityCouncilContract,
    CityCouncilExpense,
    CityCouncilRevenue,
    File,
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
from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model

logger = logging.getLogger(__name__)

CITYCOUNCIL_BID_FIELDS_MAPPING = {
    "CODLIC": "external_code",
    "CODTIPOLIC": "modality",
    "NUMLIC": "code",
    "NUMTIPOLIC": "code_type",
    "OBJETOLIC": "description",
    "DTLIC": "session_at",
    "EXCLUIDO": "excluded",
    "ARQUIVOS": None,
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


CITYCOUNCIL_REVENUE_FIELDS_MAPPING = {
    "CODLINHA": "external_code",
    "CODUNIDGESTORA": "budget_unit",
    "DTPUBLICACAO": "published_at",
    "DTREGISTRO": "registered_at",
    "TIPOREC": "revenue_type",
    "MODALIDADE": "modality",
    "DSRECEITA": "description",
    "VALOR": "value",
    "FONTE": "resource",
    "DSNATUREZA": "legal_status",  # TODO natureza do TCM-BA
    "DESTINACAO": "destination",
    "EXCLUIDO": "excluded",
}


CITYCOUNCIL_REVENUE_FUNCTIONS = {
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


CITYCOUNCIL_EXPENSE_FIELDS_MAPPING = {
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


CITYCOUNCIL_EXPENSE_FUNCTIONS = {
    "value": currency_to_float,
    "excluded": to_boolean,
    "published_at": from_str_to_date,
    "date": from_str_to_date,
    "phase": get_phase,
    "modality": lower,
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
    new_item = map_to_fields(
        item, CITYCOUNCIL_EXPENSE_FIELDS_MAPPING, CITYCOUNCIL_EXPENSE_FUNCTIONS
    )
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


def to_revenue(item):
    new_item = map_to_fields(
        item, CITYCOUNCIL_REVENUE_FIELDS_MAPPING, CITYCOUNCIL_REVENUE_FUNCTIONS
    )
    return CityCouncilRevenue(**new_item)


def to_contract_file(item):
    try:
        contract = CityCouncilContract.objects.get(external_code=item["CODCON"])
    except CityCouncilContract.DoesNotExist:
        logger.error(f"Arquivo do contrato não encontrado: {item}")
        return

    content_type = get_content_type_for_model(contract)
    url = f"{settings.CITY_COUNCIL_WEBSERVICE}{item['CAMINHO']}"
    return File(
        url=url,
        content_type=content_type,
        object_id=contract.pk,
        external_code=item["CODARQCON"],
    )


def to_bid_file(item):
    try:
        bid = CityCouncilBid.objects.get(external_code=item["CODLIC"])
    except CityCouncilBid.DoesNotExist:
        logger.error(f"Arquivo da licitação não encontrado: {item}")
        return

    content_type = get_content_type_for_model(bid)
    url = f"{settings.CITY_COUNCIL_WEBSERVICE}{item['CAMINHOARQLIC']}"
    return File(
        url=url,
        content_type=content_type,
        object_id=bid.pk,
        external_code=item["CODARQLIC"],
    )
