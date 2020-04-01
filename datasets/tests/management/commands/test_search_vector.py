from datetime import datetime
from unittest.mock import patch

import pytest
from django.test import TestCase

from datasets.management.commands._gazette import save_gazette
from datasets.management.commands.searchvector import Command
from datasets.models import Gazette


class TestCommandHandler(TestCase):
    @patch.object(Gazette.objects, "update")
    @patch("jarbas.core.management.commands.searchvector.print")
    def test_handler(self, print_, update):
        command = Command()
        command.handle()
        self.assertEqual(3, print_.call_count)
        self.assertEqual(1, update.call_count)

    @pytest.mark.django_db
    def test_create_vector(self):
        items = [
            {
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
                "file_content": "O Prefeito Municipal de Feira de Santana",
            },
            {
                "date": datetime(2019, 11, 6),
                "power": "executivo",
                "year_and_edition": "Ano V - Edi\u00e7\u00e3o N\u00ba 1131",
                "crawled_at": datetime(2019, 10, 10, 10, 11, 19),
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
                "file_content": "O Prefeito Municipal de Salvador",
            },
        ]

        saved = [save_gazette(item) for item in items]

        command = Command()
        command.handle()

        assert len(saved) == 5
