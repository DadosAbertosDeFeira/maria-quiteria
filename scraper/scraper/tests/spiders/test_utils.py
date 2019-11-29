import pytest

from scraper.scraper.spiders.utils import replace_query_param


@pytest.mark.parametrize('old_url,field,value,new_url', [
    (
        "http://www.diariooficial.feiradesantana.ba.gov.br/abrir.asp?edi=590&p=1",
        "p",
        999,
        "http://www.diariooficial.feiradesantana.ba.gov.br/abrir.asp?edi=590&p=999",
    ),
    (
        "http://www.diariooficial.feiradesantana.ba.gov.br/detalhes.asp?acao=&p=1116"
        "&menu=&idsec=1&tipo=&publicacao=1&st=&rad=&txtlei=''&dtlei=''&dtlei1=''"
        "&edicao=&hom=&ini=&fim=&meshom=#links>",
        "publicacao",
        "88",
        "http://www.diariooficial.feiradesantana.ba.gov.br/detalhes.asp?acao=&p=1116"
        "&menu=&idsec=1&tipo=&publicacao=88&st=&rad=&txtlei=''&dtlei=''&dtlei1=''"
        "&edicao=&hom=&ini=&fim=&meshom=#links>"
    ),
    (
        "detalhes.asp?acao=&p=991&menu=&idsec=1&tipo=&publicacao=1&st=&rad="
        "&txtlei=''&dtlei=''&dtlei1=''&edicao=&hom=&ini=&fim=&meshom=#links",
        "p",
        "",
        "detalhes.asp?acao=&p=&menu=&idsec=1&tipo=&publicacao=1&st=&rad="
        "&txtlei=''&dtlei=''&dtlei1=''&edicao=&hom=&ini=&fim=&meshom=#links",
    )
])
def test_replace_query_parameter_from_a_url(old_url, field, value, new_url):
    assert replace_query_param(old_url, field, value) == new_url
