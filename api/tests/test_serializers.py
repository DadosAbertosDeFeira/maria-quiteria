from datetime import datetime

import pytest
from api.serializers import CityCouncilAgendaSerializer

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
            == datetime.strptime(data["date"], "%Y-%m-%d").date()
        )
        assert serializer.validated_data["details"] == data["details"]
        assert serializer.validated_data["event_type"] == data["event_type"]
        assert serializer.validated_data["title"] == data["title"]
        assert serializer.validated_data["crawled_at"] == datetime.fromisoformat(
            data["crawled_at"]
        )
        assert serializer.validated_data["crawled_from"] == data["crawled_from"]
