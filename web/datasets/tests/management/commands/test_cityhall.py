from datetime import datetime

import pytest
from django.utils.timezone import make_aware

from web.datasets.management.commands._cityhall import save_bid


@pytest.mark.django_db
class TestSaveBid:
    def test_save_bid(self, mock_backup_file):
        item = {
            "hash_commit": "6f643054bd75871e9db6e16e2ad58ead84567c9f",
            "crawled_at": make_aware(datetime(2020, 3, 21, 7, 15, 17, 908831)),
            "crawled_from": "http://www.feiradesantana.ba.gov.br/servicos.asp",
            "session_at": make_aware(datetime(2018, 4, 17, 8, 30, 0)),
            "public_agency": "PMFS",
            "month": 4,
            "year": 2018,
            "description": (
                "Aquisi\u00e7\u00e3o de arma de fogo longa para a "
                "Guarda Municipal de Feira de Santana.OBS: EDITAL DISPON\u00cdVEL"
                "NO SITE: WWW.BLLCOMPRAS.ORG.BR"
            ),
            "history": [],
            "codes": (
                "Licita\u00e7\u00e3o 133-2018 / " "Preg\u00e3o Eletr\u00f4nico 047-2018"
            ),
            "modality": "pregao_eletronico",
            "files": [
                {
                    "url": "http://www.feiradesantana.ba.gov.br/servicos.asp?id=2",
                    "checksum": "checksum",
                    "content": None,
                }
            ],
        }

        bid = save_bid(item)
        assert bid.session_at == item["session_at"]
        assert bid.description == item["description"]
        assert bid.public_agency == item["public_agency"]
        assert bid.modality == item["modality"]
        assert bid.files
        assert bid.hash_commit == item["hash_commit"]

    def test_save_history(self, mock_backup_file):
        item = {
            "hash_commit": "6f643054bd75871e9db6e16e2ad58ead84567c9f",
            "public_agency": "PMFS",
            "crawled_at": make_aware(datetime(2020, 4, 4, 14, 29, 49, 261985)),
            "crawled_from": "http://www.feiradesantana.ba.gov.br/servicos.asp",
            "session_at": make_aware(datetime(2019, 4, 5, 8, 30)),
            "description": (
                "Contratação de empresa para prestação de serviços "
                "profissionais de apoio administrativo em Unidades de Saúde da "
                "Secretaria Municipal de Saúde.Edital disponível no site do "
                "Banco do Brasil: www.licitacoes-e.com.br.Código "
                "Correspondente Banco do Brasil: nº 755980REMARCADA"
            ),
            "codes": (
                "Licita\u00e7\u00e3o 133-2018 / " "Preg\u00e3o Eletr\u00f4nico 047-2018"
            ),
            "modality": "pregao_eletronico",
            "history": [
                {
                    "published_at": make_aware(datetime(2018, 4, 17, 8, 30, 0)),
                    "event": "Resposta a pedido de esclarecimento",
                    "url": "http://www.feiradesantana.ba.gov.br/SMS.pdf",
                }
            ],
        }
        bid = save_bid(item)
        assert bid.events.count() == 1
        event = bid.events.first()

        assert event.published_at is not None
        assert event.summary == item["history"][0]["event"]
        assert event.files.count() == 1

    def test_handle_with_existent_event(self, mock_backup_file):
        item = {
            "hash_commit": "6f643054bd75871e9db6e16e2ad58ead84567c9f",
            "public_agency": "PMFS",
            "crawled_at": make_aware(datetime(2020, 4, 4, 14, 29, 49, 261985)),
            "crawled_from": "http://www.feiradesantana.ba.gov.br/servicos.asp",
            "session_at": make_aware(datetime(2019, 4, 5, 8, 30)),
            "description": (
                "Contratação de empresa para prestação de serviços "
                "profissionais de apoio administrativo em Unidades de Saúde da "
                "Secretaria Municipal de Saúde.Edital disponível no site do "
                "Banco do Brasil: www.licitacoes-e.com.br.Código "
                "Correspondente Banco do Brasil: nº 755980REMARCADA"
            ),
            "codes": (
                "Licita\u00e7\u00e3o 133-2018 / " "Preg\u00e3o Eletr\u00f4nico 047-2018"
            ),
            "modality": "pregao_eletronico",
            "history": [
                {
                    "published_at": make_aware(datetime(2019, 4, 4, 16, 20, 0)),
                    "event": "Resposta a pedido de esclarecimento",
                    "url": "http://www.feiradesantana.ba.gov.br/SMS.pdf",
                }
            ],
        }
        bid = save_bid(item)
        assert bid.events.count() == 1

        item["history"] = [
            {
                "published_at": make_aware(datetime(2019, 4, 4, 16, 20, 0)),
                "event": "Resposta a pedido de esclarecimento",
                "url": "http://www.feiradesantana.ba.gov.br/SMS.pdf",
            },
            {
                "published_at": make_aware(datetime(2019, 4, 4, 18, 20, 0)),
                "event": "Resposta a pedido de esclarecimento",
                "url": "http://www.feiradesantana.ba.gov.br/SMS.pdf",
            },
            {
                "published_at": make_aware(datetime(2019, 4, 4, 16, 20, 0)),
                "event": "CORREÇÃO DE EDITAL",
                "url": "http://www.feiradesantana.ba.gov.br/SMS.pdf",
            },
        ]

        save_bid(item)
        assert bid.events.count() == 3

    def test_handle_with_updated_bid(self, mock_backup_file):
        item = {
            "hash_commit": "6f643054bd75871e9db6e16e2ad58ead84567c9f",
            "crawled_at": make_aware(datetime(2020, 3, 21, 7, 15, 17, 908831)),
            "crawled_from": "http://www.feiradesantana.ba.gov.br/servicos.asp",
            "session_at": make_aware(datetime(2018, 4, 17, 8, 30, 0)),
            "public_agency": "PMFS",
            "month": 4,
            "year": 2018,
            "description": (
                "Aquisi\u00e7\u00e3o de arma de fogo longa para a "
                "Guarda Municipal de Feira de Santana.OBS: EDITAL DISPON\u00cdVEL"
                "NO SITE: WWW.BLLCOMPRAS.ORG.BR"
            ),
            "history": [],
            "codes": (
                "Licita\u00e7\u00e3o 133-2018 / " "Preg\u00e3o Eletr\u00f4nico 047-2018"
            ),
            "modality": "pregao_eletronico",
            "files": [
                {
                    "url": "http://www.feiradesantana.ba.gov.br/servicos.asp?id=2",
                    "checksum": "checksum",
                    "content": None,
                }
            ],
        }

        bid = save_bid(item)

        item["description"] = "Aquisição de arma de flores."

        updated_bid = save_bid(item)

        assert bid.pk == updated_bid.pk
        assert bid.description != updated_bid.description

    def test_create_different_bids_for_different_agency_modality(
        self, mock_backup_file
    ):
        item = {
            "hash_commit": "6f643054bd75871e9db6e16e2ad58ead84567c9f",
            "crawled_at": make_aware(datetime(2020, 3, 21, 7, 15, 17, 908831)),
            "crawled_from": "http://www.feiradesantana.ba.gov.br/servicos.asp",
            "session_at": make_aware(datetime(2018, 4, 17, 8, 30, 0)),
            "public_agency": "PMFS",
            "month": 4,
            "year": 2018,
            "description": (
                "Aquisi\u00e7\u00e3o de arma de fogo longa para a "
                "Guarda Municipal de Feira de Santana.OBS: EDITAL DISPON\u00cdVEL"
                "NO SITE: WWW.BLLCOMPRAS.ORG.BR"
            ),
            "history": [],
            "codes": (
                "Licita\u00e7\u00e3o 133-2018 / " "Preg\u00e3o Eletr\u00f4nico 047-2018"
            ),
            "modality": "pregao_eletronico",
            "files": [
                {
                    "url": "http://www.feiradesantana.ba.gov.br/servicos.asp?id=2",
                    "checksum": "checksum",
                    "content": None,
                }
            ],
        }

        bid = save_bid(item)

        item["public_agency"] = "FHFS"
        item["codes"] = "CHAMADA PÚBLICA 004-2019"

        another_bid = save_bid(item)

        assert bid.pk != another_bid.pk
