from datetime import date, datetime

import pytest
from dateutil.parser import parse
from model_bakery import baker
from web.api.serializers import (
    CityCouncilAgendaSerializer,
    CityCouncilAttendanceListSerializer,
    CityCouncilMinuteSerializer,
    CityHallBidEventSerializer,
    CityHallBidSerializer,
    FileSerializer,
)

pytestmark = pytest.mark.django_db


class TestCityCouncilAgendaSerializer:
    def test_city_council_agenda_serializer(self):
        data = {
            "date": "2020-03-18",
            "details": "PROJETOS DE LEI ORDINÁRIA EM 2ª DISCUSSÃO 017/20",
            "event_type": "sessao_ordinaria",
            "title": "ORDEM DO DIA - 18 DE MARÇO DE 2020",
            "crawled_at": "2020-01-01T04:16:13-04:00",
            "crawled_from": "http://www.pudim.com.br/",
        }
        serializer = CityCouncilAgendaSerializer(data=data)

        assert serializer.is_valid()
        assert (
            serializer.validated_data["date"]
            == parse(data["date"], dayfirst=True).date()
        )
        assert serializer.validated_data["details"] == data["details"]
        assert serializer.validated_data["event_type"] == data["event_type"]
        assert serializer.validated_data["title"] == data["title"]
        assert serializer.validated_data["crawled_at"] == datetime.fromisoformat(
            data["crawled_at"]
        )
        assert serializer.validated_data["crawled_from"] == data["crawled_from"]


class TestCityCouncilAttendanceList:
    def test_city_council_attendance_list(self):
        data = {
            "date": date(2020, 12, 14),
            "description": None,
            "council_member": "Zé Curuca",
            "status": "ausente",
            "crawled_at": "2020-01-01T04:16:13-03:00",
            "crawled_from": (
                "https://www.feiradesantana.ba.leg.br/"
                "lista-presenca-vereadores/107/14-12-2020"
            ),
            "notes": "-",
        }

        serializer = CityCouncilAttendanceListSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["date"] == data["date"]
        assert serializer.validated_data["description"] == data["description"]
        assert serializer.validated_data["council_member"] == data["council_member"]
        assert serializer.validated_data["status"] == data["status"]
        assert serializer.validated_data["crawled_at"] == datetime.fromisoformat(
            data["crawled_at"]
        )
        assert serializer.validated_data["crawled_from"] == data["crawled_from"]
        assert serializer.validated_data["notes"] == data["notes"]


class TestCityCouncilMinuteSerializer:
    def test_city_council_minute_serializer(self):
        data = {
            "date": "2020-03-18",
            "event_type": "sessao_ordinaria",
            "title": "ORDEM DO DIA - 18 DE MARÇO DE 2020",
            "crawled_at": "2020-01-01T04:16:13-04:00",
            "crawled_from": "http://www.pudim.com.br/",
            "files": [
                {
                    "url": "https://www.feiradesantana.ba.leg.br/5eaabb5e91088.pd",
                    "checksum": "checksum",
                    "content": None,
                },
            ],
        }
        serializer = CityCouncilMinuteSerializer(data=data)

        assert serializer.is_valid()
        assert (
            serializer.validated_data["date"]
            == parse(data["date"], dayfirst=True).date()
        )
        assert serializer.validated_data["event_type"] == data["event_type"]
        assert serializer.validated_data["title"] == data["title"]


class TestCityHallBidEventSerializer:
    def test_city_hall_bid_event_serializer(self):
        bid = baker.make_recipe("datasets.CityHallBid")

        data = {
            "published_at": "2020-07-21T11:49:00-03:00",
            "summary": "Julgamento do recurso administrativo",
            "bid": bid.pk,
            "crawled_at": datetime.now(),
            "crawled_from": "https://www.example.com",
        }

        serializer = CityHallBidEventSerializer(data=data)
        assert serializer.is_valid()

        assert serializer.validated_data["published_at"] == datetime.fromisoformat(
            data["published_at"]
        )
        assert serializer.validated_data["summary"] == data["summary"]
        assert serializer.validated_data["bid"] == bid


class TestFileSerializer:
    def test_file_serializer(self):
        data = {"url": "https://www.example.com/file.pdf"}

        serializer = FileSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["url"] == data["url"]


class TestCityHallBidSerializer:
    def test_city_hall_bid_serializer(self):
        data = {
            "session_at": "2021-01-06T08:30:00-03:00",
            "public_agency": "PMFS",
            "description": "Contratação de empresa de engenharia",
            "modality": "convite",
            "codes": "LICITAÇÃO Nº 150-2020 TOMADA DE PREÇO Nº 038-2020",
            "crawled_at": "2020-01-01T04:16:13-04:00",
            "crawled_from": "http://www.pudim.com.br/",
            "events": [
                {
                    "id": 243,
                    "created_at": "2021-01-01T20:00:32.209476-03:00",
                    "updated_at": "2021-01-01T20:00:32.209508-03:00",
                    "crawled_at": "2021-01-01T20:00:32.185236-03:00",
                    "crawled_from": "http://www.dadosdafeira.br/teste",
                    "notes": "",
                    "published_at": "2020-07-21T11:49:00-03:00",
                    "summary": "Julgamento do recurso administrativo",
                    "bid": 315,
                },
            ],
            "files": [{"url": "http://www.dadosdafeira.br/licitacoes/testes.pdf"}],
        }

        serializer = CityHallBidSerializer(data=data)
        assert serializer.is_valid()

        assert serializer.validated_data["session_at"] == datetime.fromisoformat(
            data["session_at"]
        )
        assert serializer.validated_data["public_agency"] == data["public_agency"]
        assert serializer.validated_data["description"] == data["description"]
        assert serializer.validated_data["modality"] == data["modality"]
        assert serializer.validated_data["codes"] == data["codes"]
        assert serializer.validated_data["crawled_at"] == datetime.fromisoformat(
            data["crawled_at"]
        )
        assert serializer.validated_data["crawled_from"] == data["crawled_from"]
