from datetime import datetime

import pytest

from ..spiders.utils import (
    extract_param,
    from_str_to_datetime,
    identify_contract_id,
    replace_query_param,
)


@pytest.mark.parametrize(
    "old_url,field,value,new_url",
    [
        (
            "http://www.diariooficial.feiradesantana.ba.gov.br/"
            "abrir.asp?edi=590&p=1",
            "p",
            999,
            "http://www.diariooficial.feiradesantana.ba.gov.br/"
            "abrir.asp?edi=590&p=999",
        ),
        (
            "http://www.diariooficial.feiradesantana.ba.gov.br/"
            "detalhes.asp?acao=&p=1116&menu=&idsec=1&tipo=&publicacao"
            "=1&st=&rad=&txtlei=''&dtlei=''&dtlei1=''"
            "&edicao=&hom=&ini=&fim=&meshom=#links>",
            "publicacao",
            "88",
            "http://www.diariooficial.feiradesantana.ba.gov.br/"
            "detalhes.asp?acao=&p=1116&menu=&idsec=1&tipo="
            "&publicacao=88&st=&rad=&txtlei=''&dtlei=''&dtlei1=''"
            "&edicao=&hom=&ini=&fim=&meshom=#links>",
        ),
        (
            "detalhes.asp?acao=&p=991&menu=&idsec=1&tipo=&publicacao=1&st=&rad="
            "&txtlei=''&dtlei=''&dtlei1=''&edicao=&hom=&ini=&fim=&meshom=#links",
            "p",
            "",
            "detalhes.asp?acao=&p=&menu=&idsec=1&tipo=&publicacao=1&st=&rad="
            "&txtlei=''&dtlei=''&dtlei1=''&edicao=&hom=&ini=&fim=&meshom=#links",
        ),
    ],
)
def test_replace_query_parameter_from_a_url(old_url, field, value, new_url):
    assert replace_query_param(old_url, field, value) == new_url


@pytest.mark.parametrize(
    "text, expected_contract_id",
    [
        (" CONTRATO N�� 295-2017-10C ", "295-2017-10C"),
        ("CONTRATO N° 11-2017-10C", "11-2017-10C"),
        ("4/2016/09C", "4/2016/09C"),
        ("860/2015/05C", "860/2015/05C"),
        ("3-2017-1926C", "3-2017-1926C"),
        ("CONTRATO N�� 23820161111 ", "23820161111"),
        ("CONTRATO N° 05820171111 ", "05820171111"),
        ("CONTRATO N° 010521004-2017", "010521004-2017"),
    ],
)
def test_identify_contract_ids(text, expected_contract_id):
    assert identify_contract_id(text) == expected_contract_id


@pytest.mark.parametrize(
    "url, param, value",
    [
        (
            f"http://www.feiradesantana.ba.gov.br/seadm/servicos.asp?"
            "id=2&s=a&link=seadm/licitacoes_pm.asp&cat=PMFS&dt=01-2019#links",
            "dt",
            "01-2019",
        ),
        ("http://www.ba.gov.br/servicos.asp?dt=01-2019#links", "dt", "01-2019"),
        ("http://www.ba.gov.br/servicos.asp?dt=01-2019#links", "invalid", None),
    ],
)
def test_extract_param(url, param, value):
    assert extract_param(url, param) == value


@pytest.mark.parametrize(
    "datetime_str,expected_obj",
    [
        ("26/02/2020 19:28", datetime(2020, 2, 26, 19, 28)),
        ("26/02/2020 19:28:00", None),
        ("26/02/2020", None),
        ("26.02.20", None),
    ],
)
def test_possible_datetime_formats(datetime_str, expected_obj):
    formats = ["%d/%m/%Y %H:%M"]

    assert from_str_to_datetime(datetime_str, formats) == expected_obj


@pytest.mark.parametrize(
    "datetime_str,expected_obj",
    [
        ("26/02/20", datetime(2020, 2, 26)),
        ("26/02/2020", datetime(2020, 2, 26)),
        ("26/02/2020 19:28", None),
        ("26.02.20", None),
    ],
)
def test_possible_date_formats(datetime_str, expected_obj):
    formats = ["%d/%m/%Y", "%d/%m/%y"]

    assert from_str_to_datetime(datetime_str, formats) == expected_obj
