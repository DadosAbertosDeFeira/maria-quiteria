import logging
import urllib
from datetime import datetime
from pathlib import Path

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
        cleaned_value = value.replace("R$", "").replace(".", "").replace(",", ".")
        return float(cleaned_value)
    except ValueError:
        pass
    return


def to_boolean(value):
    return value.lower() in ["y", "s", 1]


def from_str_to_datetime(date_str, supported_formats=None):
    if supported_formats is None:
        supported_formats = [
            "%d/%m/%Y %H:%M",
            "%d/%m/%y %H:%M",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%y %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %Hh%M",
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


def from_str_to_date(date_str, supported_formats=["%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"]):
    if date_str is None:
        return
    datetime_obj = from_str_to_datetime(date_str, supported_formats)
    if datetime_obj:
        return datetime_obj.date()


def lower(value):
    return value.lower()


def modality_mapping_from_city_council_db(code):
    mapping = {
        "1": "pregao_eletronico",
        "2": "convite",
        "3": "concorrencia",
        "4": "tomada_de_precos",
        "5": "concurso",
        "6": "leilao",
        "7": "pregao_presencial",
        "9": "inexigibilidade",
        "8": "dispensada",
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


def extract_params(s3_filepath):
    """Extrai mês, ano e periodicidade do caminho do bucket."""
    prefix = "tcmbapublicconsultation/"
    start_index = s3_filepath.find(prefix) + len(prefix)
    relative_path = Path(s3_filepath[start_index:])
    folders = relative_path.parts
    year = folders[0]
    period = folders[1]
    month = None
    if period == "mensal":
        month = folders[2]
    return {"year": year, "period": period, "month": month}


def build_s3_path(s3_filepath, unit, category, filename):
    """
    Input:
    maria-quiteria/files/tcmbapublicconsultation/2020/mensal/12/consulta-publica-12-2020.json

    Output:
    s3://dadosabertosdefeira/maria-quiteria/files/tcmbapublicconsultation/2020/mensal/12/<unit>/<category>/<filename>
    """
    prefix = "s3://dadosabertosdefeira/"
    parts = s3_filepath.split("/")
    parts.pop()  # remove json da lista
    parts.extend([unit, category, filename])
    return f"{prefix}{'/'.join(parts)}"


def build_s3_url(s3_filepath):
    """
    Input:
    maria-quiteria/files/tcmbapublicconsultation/2020/mensal/12/<unit>/<category>/<filename>

    Output:
    https://dadosabertosdefeira.s3.eu-central-1.amazonaws.com/
    maria-quiteria/files/tcmbapublicconsultation/2020/mensal/12/<unit>/<category>/<filename>
    """
    s3_url = "https://dadosabertosdefeira.s3.eu-central-1.amazonaws.com/"
    return urllib.parse.quote_plus(f"{s3_url}{s3_filepath}")


def get_original_filename(item):
    if item.get("original_filename"):
        return item["original_filename"]
    else:
        # exemplo: 1a35fd41-e463-488a-936e-a526d3afa72a-OF\u00cdCIO.pdf
        uuid4_len = 36
        return item["filename"][uuid4_len + 1 :]
