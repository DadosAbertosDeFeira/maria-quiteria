import re


def replace_query_param(url, field, value):
    return re.sub(r"{}=\d+".format(field), r"{}={}".format(field, str(value)), url)


def identify_contract_id(text):
    CONTRACT_NUMBER_PATTERN = re.compile(r"\d+[-|\/]\d{4}?[-|\/]\d+C|\d+-\d{4}|\d+")
    result = re.findall(CONTRACT_NUMBER_PATTERN, text)
    if result:
        return result[0]
