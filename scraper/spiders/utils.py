import logging
import re
import unicodedata
from datetime import datetime
from urllib.parse import parse_qs, urlparse

DOMAIN_FORMAT = re.compile(
    r"(?:^(\w{1,255}):(.{1,255})@|^)"
    r"(?:(?:(?=\S{0,253}(?:$|:))"
    r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"(?:[a-z0-9]{1,63})))"
    r"|localhost)"
    r"(:\d{1,5})?",
    re.IGNORECASE,
)


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
    if start_date.year == end_date.year:
        if start_date.month == end_date.month:
            return [(start_date.month, start_date.year)]
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


def strip_accents(string):
    if string is None:
        return
    return "".join(
        char
        for char in unicodedata.normalize("NFD", string)
        if unicodedata.category(char) != "Mn"
    )


def is_url(url):
    if not url:
        return False

    url = url.strip()

    if len(url) > 2048:
        logger.warning(
            f"URL ultrapassa limite de 2048 caracteres (tamanho = {len(url)})"
        )
        return False

    result = urlparse(url)
    scheme = result.scheme
    domain = result.netloc

    if not scheme:
        logger.warning("Nenhum URL scheme especificado")
        return is_url(f"http://{url}")

    if not domain:
        logger.warning("Nenhum domínio especificado")
        return False

    if not re.fullmatch(DOMAIN_FORMAT, domain):
        logger.warning(f"Domínio inválido ({domain})")
        return False

    return True
