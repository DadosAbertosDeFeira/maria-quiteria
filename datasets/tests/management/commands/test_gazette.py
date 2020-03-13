from datetime import datetime

import pytest
from datasets.management.commands._gazette import save_gazette


@pytest.mark.django_db
def test_save_gazette():
    item = {
        "date": datetime(2019, 11, 5),
        "power": "executivo",
        "year_and_edition": "Ano V - Edi\u00e7\u00e3o N\u00ba 1131",
        "crawled_at": datetime.now(),
        "crawled_from": "http://www.diariooficial.br/st=1&publicacao=1&edicao=1131",
        "event_title": "DECRETO INDIVIDUAL N\u00ba 1.294/2019",
        "event_secretariat": "Gabinete do Prefeito",
        "event_summary": "ÍCARO IVVIN DE ALMEIDA COSTA LIMA - NOMEIA",
        "file_urls": [
            "http://www.diariooficial.feiradesantana.ba.gov.br/1VFJCB4112019.pdf"
        ],
        "content": "O Prefeito Municipal de Feira no uso de suas atribuições...",
    }

    gazette, event = save_gazette(item)
    assert event.gazette == gazette


@pytest.mark.django_db
def test_handle_with_changed_gazettes():
    item = {
        "date": datetime(2019, 11, 5),
        "power": "executivo",
        "year_and_edition": "Ano V - Edi\u00e7\u00e3o N\u00ba 1131",
        "crawled_at": datetime.now(),
        "crawled_from": "http://www.diariooficial.br/st=1&publicacao=1&edicao=1131",
        "event_title": "DECRETO INDIVIDUAL N\u00ba 1.294/2019",
        "event_secretariat": "Gabinete do Prefeito",
        "event_summary": "ÍCARO IVVIN DE ALMEIDA COSTA LIMA - NOMEIA",
        "file_urls": [
            "http://www.diariooficial.feiradesantana.ba.gov.br/1VFJCB4112019.pdf"
        ],
        "content": "O Prefeito Municipal de Feira no uso de suas atribuições...",
    }

    gazette, event = save_gazette(item)
    item["content"] = "O Prefeito no uso de suas atribuições..."
    updated_gazette, updated_event = save_gazette(item)

    assert gazette.pk == updated_gazette.pk
    assert event.pk == updated_event.pk


@pytest.mark.django_db
def test_handle_with_changed_events():
    item = {
        "date": datetime(2019, 11, 5),
        "power": "executivo",
        "year_and_edition": "Ano V - Edi\u00e7\u00e3o N\u00ba 1131",
        "crawled_at": datetime.now(),
        "crawled_from": "http://www.diariooficial.br/st=1&publicacao=1&edicao=1131",
        "event_title": "DECRETO INDIVIDUAL N\u00ba 1.294/2019",
        "event_secretariat": "Gabinete do Prefeito",
        "event_summary": "ÍCARO IVVIN DE ALMEIDA COSTA LIMA - NOMEIA",
        "file_urls": [
            "http://www.diariooficial.feiradesantana.ba.gov.br/1VFJCB4112019.pdf"
        ],
        "content": "O Prefeito Municipal de Feira no uso de suas atribuições...",
    }

    gazette, event = save_gazette(item)
    item["event_summary"] = "NOMEIA alguém"
    item["content"] = "O Prefeito no uso de suas atribuições..."
    updated_gazette, updated_event = save_gazette(item)

    assert gazette.pk == updated_gazette.pk
    assert event.pk != updated_event.pk
