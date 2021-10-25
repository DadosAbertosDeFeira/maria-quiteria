import os
from datetime import date, datetime

import pytest

from ..spiders.utils import (
    extract_date,
    extract_param,
    get_git_commit,
    identify_contract_id,
    is_url,
    months_and_years,
    replace_query_param,
    strip_accents,
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
            "http://www.feiradesantana.ba.gov.br/seadm/servicos.asp?"
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
    "start_date,end_date,expected_month_and_year",
    [
        (datetime(2020, 1, 10), datetime(2020, 3, 1), [(2, 2020), (3, 2020)]),
        (
            datetime(2019, 10, 1),
            datetime(2020, 3, 1),
            [(11, 2019), (12, 2019), (1, 2020), (2, 2020), (3, 2020)],
        ),
        (datetime(2020, 2, 10), datetime(2020, 3, 1), [(3, 2020)]),
        (datetime(2020, 6, 1), datetime(2020, 3, 1), []),
        (
            datetime(2008, 10, 11),
            datetime(2012, 3, 29),
            [(11, 2008), (12, 2008)]
            + [(m, y) for y in range(2009, 2012) for m in range(1, 13)]
            + [(1, 2012), (2, 2012), (3, 2012)],
        ),
        (datetime(2020, 4, 14), datetime(2020, 4, 23), [(4, 2020)]),
    ],
)
def test_months_and_years(start_date, end_date, expected_month_and_year):
    assert months_and_years(start_date, end_date) == expected_month_and_year


@pytest.mark.parametrize(
    "str_with_date,expected_obj",
    [
        ("26/02/2020", date(2020, 2, 26)),
        ("26/02/2020 19:28", date(2020, 2, 26)),
        ("26/02/20", date(2020, 2, 26)),
        ("26.02.20", None),
        ("Random", None),
    ],
)
def test_extract_date(str_with_date, expected_obj):
    assert extract_date(str_with_date) == expected_obj


@pytest.mark.parametrize(
    "original_value,expected_value",
    [
        ("tomada", "tomada"),
        ("pregão presencial", "pregao presencial"),
        ("pregão eletrônico", "pregao eletronico"),
        ("concorrência", "concorrencia"),
        ("çãôéà", "caoea"),
        (None, None),
    ],
)
def test_strip_accents(original_value, expected_value):
    assert strip_accents(original_value) == expected_value


@pytest.mark.parametrize(
    "original_value,expected_value",
    [
        ("google.com", True),
        ("www.google", True),
        ("feiraeh.top", True),
        ("http://feiradesantana.com.br", True),
        ("https://feiradesantana.com.br", True),
        ("https://feiradesantana.com.br", True),
        ("http://www.feiradesantana.com.br", True),
        ("https://www.feiradesantana.com.br", True),
        ("https://monitor.dadosabertosdefeira.com.br", True),
        ("http://www.feiradesantana.ba.gov.br/Word - Port20130001.pdf", True),
        ("tel:42384248", False),
        ("bobagem", False),
        ("#", False),
        (None, False),
    ],
)
def test_is_url(original_value, expected_value):
    assert is_url(original_value) is expected_value


def test_get_git_commit():
    os.environ["GIT_REV"] = "43fb0339d3758204cef63d3bc3ffadfda9b8dd3b"

    git_commit = get_git_commit()

    assert len(git_commit) == 40
    assert git_commit == "43fb0339d3758204cef63d3bc3ffadfda9b8dd3b"
