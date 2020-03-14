from datetime import datetime

import pytest
from datasets.management.commands._gazette import save_gazette


@pytest.mark.django_db
def test_save_gazette():
    item = {
        "date": datetime(2019, 11, 5),
        "power": "executivo",
        "year_and_edition": "Ano V - Edi\u00e7\u00e3o N\u00ba 1131",
        "crawled_at": datetime(2019, 11, 6, 10, 11, 19),
        "crawled_from": "http://www.diariooficial.br/st=1&publicacao=1&edicao=1131",
        "events": [
            {
                "title": "DECRETO INDIVIDUAL N\u00ba 1.294/2019",
                "secretariat": "Gabinete do Prefeito",
                "summary": "ÍCARO IVVIN DE ALMEIDA COSTA LIMA - NOMEIA",
            }
        ],
        "file_urls": [
            "http://www.diariooficial.feiradesantana.ba.gov.br/1VFJCB4112019.pdf"
        ],
        "file_content": "O Prefeito Municipal de Feira no uso de suas atribuições...",
    }

    gazette = save_gazette(item)
    assert gazette.date == item["date"]
    assert gazette.power == item["power"]
    assert gazette.year_and_edition == item["year_and_edition"]
    assert gazette.crawled_at.replace(tzinfo=None) == item["crawled_at"]
    assert gazette.crawled_from == item["crawled_from"]
    assert gazette.file_content == item["file_content"]
    assert gazette.file_urls == item["file_urls"]

    event = gazette.gazetteevent_set.first()
    assert event.title == item["events"][0]["title"]
    assert event.secretariat == item["events"][0]["secretariat"]
    assert event.summary == item["events"][0]["summary"]


@pytest.mark.django_db
def test_handle_with_changed_gazettes():
    item = {
        "date": datetime(2019, 11, 5),
        "power": "executivo",
        "year_and_edition": "Ano V - Edi\u00e7\u00e3o N\u00ba 1131",
        "crawled_at": datetime(2019, 11, 6, 10, 11, 19),
        "crawled_from": "http://www.diariooficial.br/st=1&publicacao=1&edicao=1131",
        "events": [
            {
                "title": "DECRETO INDIVIDUAL N\u00ba 1.294/2019",
                "secretariat": "Gabinete do Prefeito",
                "summary": "ÍCARO IVVIN DE ALMEIDA COSTA LIMA - NOMEIA",
            }
        ],
        "file_urls": [
            "http://www.diariooficial.feiradesantana.ba.gov.br/1VFJCB4112019.pdf"
        ],
        "file_content": "O Prefeito Municipal de Feira no uso de suas atribuições...",
    }

    gazette = save_gazette(item)
    item["file_content"] = "O Prefeito no uso de suas atribuições..."
    updated_gazette = save_gazette(item)

    assert gazette.pk == updated_gazette.pk


@pytest.mark.django_db
def test_save_different_events_to_same_gazette():
    item = {
        "date": datetime(2019, 11, 5),
        "power": "executivo",
        "year_and_edition": "Ano V - Edi\u00e7\u00e3o N\u00ba 1131",
        "crawled_at": datetime(2019, 11, 6, 10, 11, 19),
        "crawled_from": "http://www.diariooficial.br/st=1&publicacao=1&edicao=1131",
        "events": [
            {
                "title": "DECRETO INDIVIDUAL N\u00ba 1.294/2019",
                "secretariat": "Gabinete do Prefeito",
                "summary": "ÍCARO IVVIN DE ALMEIDA COSTA LIMA - NOMEIA",
            },
            {
                "title": "Outro título aleatório",
                "secretariat": "Gabinete do Prefeito",
                "summary": "ÍCARO IVVIN DE ALMEIDA COSTA LIMA - NOMEIA",
            },
        ],
        "file_urls": [
            "http://www.diariooficial.feiradesantana.ba.gov.br/1VFJCB4112019.pdf"
        ],
        "file_content": "O Prefeito Municipal de Feira no uso de suas atribuições...",
    }

    gazette = save_gazette(item)
    assert gazette.gazetteevent_set.count() == 2
