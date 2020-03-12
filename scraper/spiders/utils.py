import re
from datetime import datetime
from urllib.parse import parse_qs, urlparse


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


def from_str_to_datetime(date_str, supported_formats):
    for supported_format in supported_formats:
        try:
            return datetime.strptime(date_str, supported_format)
        except ValueError:
            pass


def from_str_to_date(date_str, supported_formats):
    return from_str_to_datetime(date_str, supported_formats).date()


def currency_from_str_to_float(money):
    """
    Parser salary with the following pattern:
    - R$ 788,00
    - R$ 2.109,74
    - R$ 0,00
    To:
    - 788.00
    - 2109.74
    - 0.00
    """
    money = re.sub(r"R[$]\s+", "", money)
    money = money.replace(".", "").replace(",", ".")
    return float(money)


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
