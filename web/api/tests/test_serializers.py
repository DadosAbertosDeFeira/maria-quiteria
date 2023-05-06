from datetime import date, datetime

import pytest
from dateutil.parser import parse
from web.api.serializers import (
    CityCouncilAgendaSerializer,
    CityCouncilAttendanceListSerializer,
    CityCouncilMinuteSerializer,
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

        assert serializer.is_valid() is True
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
        assert serializer.is_valid() is True
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

        assert serializer.is_valid() is True
        assert (
            serializer.validated_data["date"]
            == parse(data["date"], dayfirst=True).date()
        )
        assert serializer.validated_data["event_type"] == data["event_type"]
        assert serializer.validated_data["title"] == data["title"]
