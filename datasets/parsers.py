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


def from_str_to_datetime(date_str, supported_formats=None):
    if supported_formats is None:
        supported_formats = [
            "%d/%m/%Y %H:%M",
            "%d/%m/%y %H:%M",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%y %H:%M:%S",
        ]
    if date_str:
        for supported_format in supported_formats:
            try:
                converted_date = datetime.strptime(date_str, supported_format)
            except ValueError:
                pass
            else:
                reference_date = datetime(1833, 9, 18)
                if converted_date >= reference_date:
                    return converted_date


def from_str_to_date(date_str, supported_formats=["%d/%m/%Y", "%d/%m/%y"]):
    if date_str is None:
        return
    datetime_obj = from_str_to_datetime(date_str, supported_formats)
    if datetime_obj:
        return datetime_obj.date()


def lower(value):
    return value.lower()
