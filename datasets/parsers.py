from datetime import datetime


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
        cleaned_value = value.replace("R$", "").replace(".", "").replace(",", ".")
        return float(cleaned_value)
    except ValueError:
        pass
    return


def to_boolean(value):
    return value.lower() in ["y", "S", 1]


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


def lower(value):
    return value.lower()
