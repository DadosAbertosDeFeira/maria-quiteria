import logging
import unicodedata
from datetime import datetime

from dateutil.parser import ParserError, parse

logger = logging.getLogger(__name__)


def get_phase(value):
    mapping = {
        "emp": "empenho",
        "liq": "liquidacao",
        "pag": "pagamento",
    }
    return mapping.get(value.lower().strip(), None)


def currency_to_float(value):
    """Converte de R$ 69.848,70 (str) para 69848.70 (float)."""
    try:
        # format 37500.36 or '37500.36
        return float(value.replace("'", ""))
    except ValueError:
        # format R$ 37.500,36 or 37.500,36
        cleaned_value = value.replace("R$", "").replace(".", "").replace(",", ".")
        try:
            return float(cleaned_value)
        except ValueError:
            pass
    return


def to_boolean(value):
    return value.lower() in ["y", "s", 1]


def from_str_to_datetime(date_str, supported_formats=None):
    if date_str is None:
        return
    try:
        converted_date = parse(date_str, dayfirst=True)
    except ParserError:
        pass
    else:
        reference_date = datetime(1833, 9, 18)
        if converted_date >= reference_date:
            return converted_date
    return


def from_str_to_date(date_str, supported_formats=["%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"]):
    if date_str is None:
        return
    datetime_obj = from_str_to_datetime(date_str, supported_formats)
    if datetime_obj:
        return datetime_obj.date()


def lower(value):
    if value:
        return value.lower()


def lower_without_spaces(value):
    if value:
        return strip_accents(value.lower()).replace(" ", "_")


def city_council_bid_modality_mapping(code):
    mapping = {
        "1": "pregao_eletronico",
        "2": "convite",
        "3": "concorrencia",
        "4": "tomada_de_precos",
        "5": "concurso",
        "6": "leilao",
        "7": "pregao_presencial",
        "8": "dispensada",
        "9": "inexigibilidade",
    }
    found = mapping.get(code)
    if found:
        return found
    else:
        logger.warning(f"Código da modalidade não encontrado: {code}")


def city_council_revenue_type_mapping(code):
    mapping = {
        "ORC": "orcamentaria",
        "NORC": "nao_orcamentaria",
        "TRANSF": "transferencia",
    }
    found = mapping.get(code)
    if found:
        return found
    else:
        logger.warning(f"Código da tipo de receita não encontrado: {code}")


def strip_accents(string):
    if string is None:
        return
    return "".join(
        char
        for char in unicodedata.normalize("NFD", string)
        if unicodedata.category(char) != "Mn"
    )
