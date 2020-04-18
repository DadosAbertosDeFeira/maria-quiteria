from datetime import datetime

import pytest
from datasets.management.commands._cityhall import save_bid


@pytest.mark.django_db
class TestSaveBid:
    def test_save_bid(self):
        item = {
            "crawled_at": datetime(2020, 3, 21, 7, 15, 17, 908831),
            "crawled_from": "http://www.feiradesantana.ba.gov.br/servicos.asp",
            "date": datetime(2018, 4, 17, 8, 30, 0),
            "category": "PMFS",
            "month": 4,
            "year": 2018,
            "description": (
                "Aquisi\u00e7\u00e3o de arma de fogo longa para a "
                "Guarda Municipal de Feira de Santana.OBS: EDITAL DISPON\u00cdVEL"
                "NO SITE: WWW.BLLCOMPRAS.ORG.BR"
            ),
            "history": [],
            "modality": (
                "Licita\u00e7\u00e3o 133-2018 / " "Preg\u00e3o Eletr\u00f4nico 047-2018"
            ),
            "file_urls": ["http://www.feiradesantana.ba.gov.br/servicos.asp?id=2"],
            "file_content": "Bla bla bla",
        }

        bid = save_bid(item)
        assert bid.date == item["date"]
        assert bid.description == item["description"]
        assert bid.category == item["category"]
        assert bid.modality == item["modality"]
        assert bid.file_url == item["file_urls"][0]
        assert bid.file_content == item["file_content"]

    def test_save_history(self):
        item = {
            "category": "PMFS",
            "crawled_at": datetime(2020, 4, 4, 14, 29, 49, 261985),
            "crawled_from": "http://www.feiradesantana.ba.gov.br/servicos.asp",
            "date": datetime(2019, 4, 5, 8, 30),
            "description": (
                "Contratação de empresa para prestação de serviços "
                "profissionais de apoio administrativo em Unidades de Saúde da "
                "Secretaria Municipal de Saúde.Edital disponível no site do "
                "Banco do Brasil: www.licitacoes-e.com.br.Código "
                "Correspondente Banco do Brasil: nº 755980REMARCADA"
            ),
            "modality": (
                "Licita\u00e7\u00e3o 133-2018 / " "Preg\u00e3o Eletr\u00f4nico 047-2018"
            ),
            "history": [
                {
                    "date": datetime(2019, 4, 4, 16, 20, 0),
                    "event": "Resposta a pedido de esclarecimento",
                    "url": "http://www.feiradesantana.ba.gov.br/SMS.pdf",
                }
            ],
        }
        bid = save_bid(item)
        assert bid.events.count() == 1
        event = bid.events.first()

        assert event.date == item["history"][0]["date"]
        assert event.summary == item["history"][0]["event"]
        assert event.file_url == item["history"][0]["url"]

    def test_handle_with_existent_event(self):
        item = {
            "category": "PMFS",
            "crawled_at": datetime(2020, 4, 4, 14, 29, 49, 261985),
            "crawled_from": "http://www.feiradesantana.ba.gov.br/servicos.asp",
            "date": datetime(2019, 4, 5, 8, 30),
            "description": (
                "Contratação de empresa para prestação de serviços "
                "profissionais de apoio administrativo em Unidades de Saúde da "
                "Secretaria Municipal de Saúde.Edital disponível no site do "
                "Banco do Brasil: www.licitacoes-e.com.br.Código "
                "Correspondente Banco do Brasil: nº 755980REMARCADA"
            ),
            "modality": (
                "Licita\u00e7\u00e3o 133-2018 / " "Preg\u00e3o Eletr\u00f4nico 047-2018"
            ),
            "history": [
                {
                    "date": datetime(2019, 4, 4, 16, 20, 0),
                    "event": "Resposta a pedido de esclarecimento",
                    "url": "http://www.feiradesantana.ba.gov.br/SMS.pdf",
                }
            ],
        }
        bid = save_bid(item)
        assert bid.events.count() == 1

        item["history"] = [
            {
                "date": datetime(2019, 4, 4, 16, 20, 0),
                "event": "Resposta a pedido de esclarecimento",
                "url": "http://www.feiradesantana.ba.gov.br/SMS.pdf",
            },
            {
                "date": datetime(2019, 4, 4, 18, 20, 0),
                "event": "Resposta a pedido de esclarecimento",
                "url": "http://www.feiradesantana.ba.gov.br/SMS.pdf",
            },
            {
                "date": datetime(2019, 4, 4, 16, 20, 0),
                "event": "CORREÇÃO DE EDITAL",
                "url": "http://www.feiradesantana.ba.gov.br/SMS.pdf",
            },
        ]

        save_bid(item)
        assert bid.events.count() == 3

    def test_handle_with_updated_bid(self):
        item = {
            "crawled_at": datetime(2020, 3, 21, 7, 15, 17, 908831),
            "crawled_from": "http://www.feiradesantana.ba.gov.br/servicos.asp",
            "date": datetime(2018, 4, 17, 8, 30, 0),
            "category": "PMFS",
            "month": 4,
            "year": 2018,
            "description": (
                "Aquisi\u00e7\u00e3o de arma de fogo longa para a "
                "Guarda Municipal de Feira de Santana.OBS: EDITAL DISPON\u00cdVEL"
                "NO SITE: WWW.BLLCOMPRAS.ORG.BR"
            ),
            "history": [],
            "modality": (
                "Licita\u00e7\u00e3o 133-2018 / " "Preg\u00e3o Eletr\u00f4nico 047-2018"
            ),
            "file_urls": ["http://www.feiradesantana.ba.gov.br/servicos.asp?id=2"],
            "file_content": "Bla bla bla",
        }

        bid = save_bid(item)

        item["description"] = "Aquisição de arma de flores."

        updated_bid = save_bid(item)

        assert bid.pk == updated_bid.pk
        assert bid.description != updated_bid.description

    def test_create_different_bids_for_different_agency_modality(self):
        item = {
            "crawled_at": datetime(2020, 3, 21, 7, 15, 17, 908831),
            "crawled_from": "http://www.feiradesantana.ba.gov.br/servicos.asp",
            "date": datetime(2018, 4, 17, 8, 30, 0),
            "category": "PMFS",
            "month": 4,
            "year": 2018,
            "description": (
                "Aquisi\u00e7\u00e3o de arma de fogo longa para a "
                "Guarda Municipal de Feira de Santana.OBS: EDITAL DISPON\u00cdVEL"
                "NO SITE: WWW.BLLCOMPRAS.ORG.BR"
            ),
            "history": [],
            "modality": (
                "Licita\u00e7\u00e3o 133-2018 / " "Preg\u00e3o Eletr\u00f4nico 047-2018"
            ),
            "file_urls": ["http://www.feiradesantana.ba.gov.br/servicos.asp?id=2"],
            "file_content": "Bla bla bla",
        }

        bid = save_bid(item)

        item["category"] = "FHFS"
        item["modality"] = "CHAMADA PÚBLICA 004-2019"

        another_bid = save_bid(item)

        assert bid.pk != another_bid.pk
