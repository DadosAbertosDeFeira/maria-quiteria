import re
import urllib.parse as urlparse
from datetime import datetime
from urllib.parse import parse_qs


def replace_query_param(url, field, value):
    return re.sub(r"{}=\d+".format(field), r"{}={}".format(field, str(value)), url)


def identify_contract_id(text):
    CONTRACT_NUMBER_PATTERN = re.compile(r"\d+[-|\/]\d{4}?[-|\/]\d+C|\d+-\d{4}|\d+")
    result = re.findall(CONTRACT_NUMBER_PATTERN, text)
    if result:
        return result[0]


def extract_param(url, param):
    parsed = urlparse.urlparse(url)
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
