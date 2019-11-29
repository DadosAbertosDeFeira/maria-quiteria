import re


def replace_query_param(url, field, value):
    return re.sub(r'{}=\d+'.format(field), r'{}={}'.format(field, str(value)), url)
