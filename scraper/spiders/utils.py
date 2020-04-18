import logging
import re
from datetime import datetime
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)


def replace_query_param(url, field, value):
    return re.sub(r"{}=\d+".format(field), r"{}={}".format(field, str(value)), url)


def identify_contract_id(text):
    CONTRACT_NUMBER_PATTERN = re.compile(r"\d+[-|\/]\d{4}?[-|\/]\d+C|\d+-\d{4}|\d+")
    result = re.findall(CONTRACT_NUMBER_PATTERN, text)
    if result:
        return result[0]


def extract_param(url, param):
    parsed = urlparse(url)
    try:
        value = parse_qs(parsed.query)[param]
        return value[0]
    except KeyError:
        return


def from_str_to_datetime(date_str, supported_formats=["%d/%m/%Y", "%d/%m/%y"]):
    if date_str is None:
        return
    for supported_format in supported_formats:
        try:
            return datetime.strptime(date_str, supported_format)
        except ValueError:
            pass


def from_str_to_date(date_str, supported_formats=["%d/%m/%Y", "%d/%m/%y"]):
    if date_str is None:
        return
    datetime_obj = from_str_to_datetime(date_str, supported_formats)
    if datetime_obj:
        return datetime_obj.date()


def months_and_years(start_date, end_date):
    pairs = []
    for year in range(start_date.year, end_date.year + 1):
        for month in range(1, 13):
            if start_date.year == end_date.year:
                if start_date.month < month <= end_date.month:
                    pairs.append((month, year))
            elif year == start_date.year:
                if month > start_date.month:
                    pairs.append((month, year))
            elif year == end_date.year:
                if month <= end_date.month:
                    pairs.append((month, year))
            elif year not in (start_date.year, end_date.year):
                pairs.append((month, year))
    return pairs


def extract_date(str_with_date):
    DATE_PATTERN = re.compile(r"\d+\/\d+\/\d+")
    result = re.search(DATE_PATTERN, str_with_date)
    if result:
        supported_formats = ["%d/%m/%Y", "%d/%m/%y"]
        return from_str_to_date(result.group(0), supported_formats)
    return


def normalize_currency(value):
    """Converte de R$ 69.848,70 (str) para 69848.70 (float)."""
    try:
        cleaned_value = value.replace("R$", "").replace(".", "").replace(",", ".")
        return float(cleaned_value)
    except ValueError:
        logging.error("Falha ao converter valor", exc_info=True)
    return


def extract_modality_and_code(raw_modality):
    """Extrai o código da licitação e a sua modalidade."""
    MODALITY_AND_CODE_PATTERN = r".* (\d+-\d+) ((.*) (\d+[-]\d+))?"
    ONLY_MODALITY_PATTERN = r"(.*) (\d+-\d+)"
    codes_and_modality = {
        "bid_code": None,
        "modality": None,
        "modality_code": None,
    }
    result = re.search(MODALITY_AND_CODE_PATTERN, raw_modality, re.IGNORECASE)
    if result and len(result.groups()) == 4:
        # formato: ('353-2019', 'PREGÃO ELETRÔNICO Nº. 219-2019', 'PREGÃO ELETRÔNICO',
        # '219-2019')
        codes_and_modality["bid_code"] = result.group(1)
        codes_and_modality["modality"] = result.group(3)
        codes_and_modality["modality_code"] = result.group(4)
    else:
        result = re.search(ONLY_MODALITY_PATTERN, raw_modality, re.IGNORECASE)
        if result:
            # formato: ('CHAMADA PÚBLICA', '004-2019')
            codes_and_modality["modality"] = result.group(1)
            codes_and_modality["modality_code"] = result.group(2)
    return codes_and_modality
