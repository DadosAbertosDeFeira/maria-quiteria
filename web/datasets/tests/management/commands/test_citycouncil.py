from datetime import date, datetime

import pytest
from django.utils.timezone import make_aware

from web.datasets.management.commands._citycouncil import (
    save_agenda,
    save_attendance_list,
    save_minute,
)


@pytest.mark.django_db
class TestSaveAgenda:
    def test_save_gazette(self):
        item = {
            "crawled_at": make_aware(datetime(2020, 3, 21, 7, 15, 17, 908831)),
            "crawled_from": "https://www.feiradesantana.ba.leg.br/agenda",
            "date": date(2019, 8, 29),
            "details": "- Especial , dia 29 (quinta-feira), às 09 horas,"
            " para apresentar a sociedade\r\n"
            "civil e aos órgãos competentes e afins, os resultados dos "
            "trabalhos\r\n"
            "desenvolvidos pela Fundação Municipal de Tecnologia da "
            "informação,\r\n"
            "Telecomunicações e Cultura Egberto Tavares Costa- FUNTITEC, "
            "atendendo ao\r\n"
            "Requerimento nº 142/2019.",
            "event_type": "sessao_especial",
            "title": "SESSÃO ESPECIAL 29 DE AGOSTO",
        }

        agenda = save_agenda(item)
        assert agenda.date == item["date"]
        assert agenda.details == item["details"]
        assert agenda.event_type == item["event_type"]
        assert agenda.title == item["title"]
        assert agenda.crawled_at == item["crawled_at"]
        assert agenda.crawled_from == item["crawled_from"]

    def test_handle_with_changed_agenda(self):
        item = {
            "crawled_at": make_aware(datetime(2020, 3, 21, 7, 15, 17, 908831)),
            "crawled_from": "https://www.feiradesantana.ba.leg.br/agenda",
            "date": date(2019, 8, 29),
            "details": "- Especial , dia 29 (quinta-feira), às 09 horas,"
            " para apresentar a sociedade\r\n"
            "civil e aos órgãos competentes e afins, os resultados dos "
            "trabalhos\r\n"
            "desenvolvidos pela Fundação Municipal de Tecnologia da "
            "informação,\r\n"
            "Telecomunicações e Cultura Egberto Tavares Costa- FUNTITEC, "
            "atendendo ao\r\n"
            "Requerimento nº 142/2019.",
            "event_type": "sessao_especial",
            "title": "SESSÃO ESPECIAL 29 DE AGOSTO",
        }

        agenda = save_agenda(item)
        item["details"] = "Festa na cidade bla bla bla"
        item["crawled_at"] = make_aware(datetime(2020, 3, 22, 7, 15, 17, 908831))

        updated_agenda = save_agenda(item)

        assert agenda.pk == updated_agenda.pk
        assert agenda.details != updated_agenda.details
        assert agenda.crawled_at != updated_agenda.crawled_at


@pytest.mark.django_db
class TestSaveAttendanceList:
    def test_save_attendance_list(self):
        item = {
            "date": date(2020, 2, 3),
            "description": "Abertura da 1ª etapa do 4º período da 18ª legislatura",
            "council_member": "Roberto Luis da Silva Tourinho",
            "status": "presente",
            "crawled_at": make_aware(datetime(2020, 3, 21, 7, 15, 17, 276019)),
            "crawled_from": "https://www.feiradesantana.ba.leg.br/lista/7/03-02-2020",
        }

        attendance = save_attendance_list(item)
        assert attendance.date == item["date"]
        assert attendance.description == item["description"]
        assert attendance.council_member == item["council_member"]
        assert attendance.status == item["status"]
        assert attendance.crawled_at == item["crawled_at"]
        assert attendance.crawled_from == item["crawled_from"]

    def test_handle_with_changed_attendance_list(self):
        item = {
            "date": date(2020, 2, 3),
            "description": "Abertura da 1ª etapa do 4º período da 18ª legislatura",
            "council_member": "Roberto Luis da Silva Tourinho",
            "status": "ausente",
            "crawled_at": make_aware(datetime(2020, 3, 21, 7, 15, 17, 276019)),
            "crawled_from": "https://www.feiradesantana.ba.leg.br/lista/7/03-02-2020",
        }

        attendance = save_attendance_list(item)
        item["status"] = "falta_justificada"
        item["crawled_at"] = make_aware(datetime(2020, 3, 22, 7, 15, 17, 908831))

        updated_attendance = save_attendance_list(item)

        assert attendance.pk == updated_attendance.pk
        assert attendance.council_member == updated_attendance.council_member
        assert attendance.description == updated_attendance.description
        assert attendance.crawled_from == updated_attendance.crawled_from
        assert attendance.status != updated_attendance.status
        assert attendance.crawled_at != updated_attendance.crawled_at


@pytest.mark.django_db
class TestSaveMinute:
    def test_save_minute(self, mock_save_file):
        item = {
            "crawled_at": make_aware(datetime(2020, 4, 30, 18, 18, 56, 173788)),
            "crawled_from": "https://www.feiradesantana.ba.leg.br/atas?"
            "mes=9&ano=2018&Acessar=OK",
            "date": date(2018, 9, 11),
            "event_type": None,
            "files": [
                {
                    "url": "https://www.feiradesantana.ba.leg.br/5eaabb5e91088.pd",
                    "checksum": "checksum",
                    "content": None,
                }
            ],
            "title": "Ata da 4ª Reunião para Instalação da Comissão Especial",
        }

        minute = save_minute(item)
        assert minute.date == item["date"]
        assert minute.title == item["title"]
        assert minute.event_type == item["event_type"]
        assert minute.crawled_from == item["crawled_from"]
