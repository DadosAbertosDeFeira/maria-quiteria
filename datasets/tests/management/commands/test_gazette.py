from datetime import date, datetime

import pytest

from datasets.management.commands._gazette import (
    _extract_date,
    save_gazette,
    save_legacy_gazette,
)


@pytest.mark.django_db
class TestSaveGazette:
    def test_save_gazette(self):
        item = {
            "date": datetime(2019, 11, 5),
            "power": "executivo",
            "year_and_edition": "Ano V - Edi\u00e7\u00e3o N\u00ba 1131",
            "crawled_at": datetime(2019, 11, 6, 10, 11, 19),
            "crawled_from": "http://www.diariooficial.br/st=1&publ=1&edicao=1131",
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
            "file_content": "O Prefeito Municipal de Feira...",
        }

        gazette = save_gazette(item)
        assert gazette.date == item["date"]
        assert gazette.power == item["power"]
        assert gazette.year_and_edition == item["year_and_edition"]
        assert gazette.crawled_at.replace(tzinfo=None) == item["crawled_at"]
        assert gazette.crawled_from == item["crawled_from"]
        assert gazette.file_content == item["file_content"]
        assert gazette.file_url == item["file_urls"][0]

        event = gazette.gazetteevent_set.first()
        assert event.title == item["events"][0]["title"]
        assert event.secretariat == item["events"][0]["secretariat"]
        assert event.summary == item["events"][0]["summary"]

        # To guarantee full text vector has been automatically created.
        gazette.refresh_from_db()
        assert gazette.search_vector == "'feir':5 'municipal':3 'prefeit':2"

    def test_handle_with_changed_gazettes(self):
        item = {
            "date": datetime(2019, 11, 5),
            "power": "executivo",
            "year_and_edition": "Ano V - Edi\u00e7\u00e3o N\u00ba 1131",
            "crawled_at": datetime(2019, 11, 6, 10, 11, 19),
            "crawled_from": "http://www.diariooficial.br/st=1&edicao=1131",
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
            "file_content": "O Prefeito Municipal de Feira...",
        }

        gazette = save_gazette(item)
        item["file_content"] = "O Prefeito no uso de suas atribuições..."
        item["crawled_at"] = datetime(2020, 3, 22, 7, 15, 17, 908831)
        updated_gazette = save_gazette(item)

        assert gazette.pk == updated_gazette.pk

    def test_save_different_events_to_same_gazette(self):
        item = {
            "date": datetime(2019, 11, 5),
            "power": "executivo",
            "year_and_edition": "Ano V - Edi\u00e7\u00e3o N\u00ba 1131",
            "crawled_at": datetime(2019, 11, 6, 10, 11, 19),
            "crawled_from": "http://www.diariooficial.br/st=1&edicao=1131",
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
            "file_content": "O Prefeito Municipal de Feira...",
        }

        gazette = save_gazette(item)
        assert gazette.gazetteevent_set.count() == 2


@pytest.mark.django_db
class TestSaveLegacyGazette:
    def test_save_legacy_gazette(self):
        legacy_item = {
            "title": "DECRETO Nº 9.416, DE 26 DE NOVEMBRO DE 2014.",
            "published_on": "Folha do Estado",
            "date": datetime(2014, 11, 27),
            "details": "ABRE CRÉDITO SUPLEMENTAR AO ORÇAMENTO DO MUNICÍPIO...",
            "file_urls": ["http://www.feiradesantana.ba.gov.br/leis/Deno20149416.pdf"],
            "file_content": "O Prefeito Municipal de Feira...",
            "crawled_at": datetime(2019, 11, 6, 10, 11, 19),
            "crawled_from": "http://www.diariooficial.br/st=1&publicacao=1&edicao=1131",
        }

        gazette = save_legacy_gazette(legacy_item)

        assert gazette.date == legacy_item["date"]
        assert gazette.power == "executivo"
        assert gazette.year_and_edition == ""
        assert gazette.is_legacy is True
        assert gazette.file_url == legacy_item["file_urls"][0]
        assert gazette.file_content == legacy_item["file_content"]
        assert gazette.crawled_at.replace(tzinfo=None) == legacy_item["crawled_at"]
        assert gazette.crawled_from == legacy_item["crawled_from"]
        assert gazette.gazetteevent_set.count() == 1

        event = gazette.gazetteevent_set.first()
        assert event.title == legacy_item["title"]
        assert event.secretariat is None
        assert event.summary == legacy_item["details"]
        assert event.published_on == legacy_item["published_on"]

    def test_save_different_events_to_same_legacy_gazette(self):
        legacy_items = [
            {
                "title": "DECRETO Nº 9.416, DE 26 DE NOVEMBRO DE 2014.",
                "published_on": "Folha do Estado",
                "date": datetime(2014, 11, 27),
                "details": "ABRE CRÉDITO SUPLEMENTAR AO ORÇAMENTO DO MUNICÍPIO...",
                "file_urls": [
                    "http://www.feiradesantana.ba.gov.br/leis/Deno20149416.pdf"
                ],
                "file_content": "O Prefeito Municipal de Feira...",
                "crawled_at": datetime(2019, 11, 6, 10, 11, 19),
                "crawled_from": "http://www.diariooficial.br/st=1&&edicao=1131",
            },
            {
                "title": "DECRETO Nº 9.415, DE 26 DE NOVEMBRO DE 2014.",
                "published_on": "Folha do Estado",
                "date": datetime(2014, 11, 27),
                "details": "ALTERA O QUADRO DE DETALHAMENTO DE DESPESA...",
                "file_urls": [
                    "http://www.feiradesantana.ba.gov.br/leis/Deno20149416.pdf"
                ],
                "file_content": "O Prefeito Municipal de Feira...",
                "crawled_at": datetime(2019, 11, 6, 10, 11, 19),
                "crawled_from": "http://www.diariooficial.br/st=1&&edicao=1131",
            },
            {
                "title": "DECRETO Nº 9.414, DE 26 DE NOVEMBRO DE 2014.",
                "published_on": "Folha do Estado",
                "date": datetime(2014, 11, 27),
                "details": "ALTERA O QUADRO DE DETALHAMENTO DE DESPESA...",
                "file_urls": [
                    "http://www.feiradesantana.ba.gov.br/leis/Deno20149416.pdf"
                ],
                "file_content": "O Prefeito Municipal de Feira...",
                "crawled_at": datetime(2019, 11, 6, 10, 11, 19),
                "crawled_from": "http://www.diariooficial.br/st=1&&edicao=1131",
            },
        ]

        gazettes = [save_legacy_gazette(legacy_item) for legacy_item in legacy_items]

        assert len(set([g.pk for g in gazettes])) == 1
        assert gazettes[0].gazetteevent_set.count() == 3

    def test_save_different_events_to_different_legacy_gazette(self):
        legacy_items = [
            {
                "title": "DECRETO Nº 9.416, DE 1 DE NOVEMBRO DE 2014.",
                "published_on": None,
                "date": None,
                "details": "ABRE CRÉDITO SUPLEMENTAR AO ORÇAMENTO DO MUNICÍPIO...",
                "file_urls": [
                    "http://www.feiradesantana.ba.gov.br/leis/Deno20149416.pdf"
                ],
                "file_content": "O Prefeito Municipal de Feira...",
                "crawled_at": datetime(2019, 11, 6, 10, 11, 19),
                "crawled_from": "http://www.diariooficial.br/?st=1&edicao=1130",
            },
            {
                "title": "DECRETO Nº 9.415, DE 26 DE NOVEMBRO DE 2014.",
                "published_on": "Folha do Estado",
                "date": datetime(2014, 11, 27),
                "details": "ALTERA O QUADRO DE DETALHAMENTO DE DESPESA...",
                "file_urls": [
                    "http://www.feiradesantana.ba.gov.br/leis/Deno20149415.pdf"
                ],
                "file_content": "O Prefeito Municipal de Feira...",
                "crawled_at": datetime(2019, 11, 6, 10, 11, 19),
                "crawled_from": "http://www.diariooficial.br/?&edicao=1131",
            },
            {
                "title": "DECRETO Nº 9.414, DE 26 DE NOVEMBRO DE 2014.",
                "published_on": "Folha do Estado",
                "date": datetime(2014, 11, 27),
                "details": "ALTERA O QUADRO DE DETALHAMENTO DE DESPESA...",
                "file_urls": [
                    "http://www.feiradesantana.ba.gov.br/leis/Deno20149414.pdf"
                ],
                "file_content": "O Prefeito Municipal de Feira...",
                "crawled_at": datetime(2019, 11, 6, 10, 11, 19),
                "crawled_from": "http://www.diariooficial.br/?&edicao=1131",
            },
        ]

        gazettes = [save_legacy_gazette(legacy_item) for legacy_item in legacy_items]

        assert len(set([g.pk for g in gazettes])) == 3
        assert gazettes[0].notes == "Data extraída do título."


class TestExtractDate:
    @pytest.mark.parametrize(
        "str_date,expected_date",
        [
            ("DECRETO Nº 9.414, DE 26 DE NOVEMBRO DE 2014.", date(2014, 11, 26)),
            ("Decreto Nº 8.140 de 14 de dezembro de 2010", date(2010, 12, 14)),
        ],
    )
    def test_extract_date(self, str_date, expected_date):
        assert _extract_date(str_date) == expected_date

    @pytest.mark.parametrize(
        "str_date",
        ["DECRETO Nº 9.414, DE NOVEMBRO DE 2014.", "DECRETO Nº 9.414", "", None],
    )
    def test_return_none_if_no_date_is_found(self, str_date):
        assert _extract_date(str_date) is None
