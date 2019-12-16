import pytest

from ..spiders.utils import identify_contract_id, replace_query_param


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
