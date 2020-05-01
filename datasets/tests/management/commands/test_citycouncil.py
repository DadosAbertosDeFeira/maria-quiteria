from datetime import date, datetime

import pytest
from datasets.management.commands._citycouncil import (
    save_agenda,
    save_attendance_list,
    save_expense,
    save_minute,
)


@pytest.mark.django_db
class TestSaveAgenda:
    def test_save_gazette(self):
        item = {
            "crawled_at": datetime(2020, 3, 21, 7, 15, 17, 908831),
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
        assert agenda.crawled_at.replace(tzinfo=None) == item["crawled_at"]
        assert agenda.crawled_from == item["crawled_from"]

    def test_handle_with_changed_agenda(self):
        item = {
            "crawled_at": datetime(2020, 3, 21, 7, 15, 17, 908831),
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
        item["crawled_at"] = datetime(2020, 3, 22, 7, 15, 17, 908831)

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
            "crawled_at": datetime(2020, 3, 21, 7, 15, 17, 276019),
            "crawled_from": "https://www.feiradesantana.ba.leg.br/lista/7/03-02-2020",
        }

        attendance = save_attendance_list(item)
        assert attendance.date == item["date"]
        assert attendance.description == item["description"]
        assert attendance.council_member == item["council_member"]
        assert attendance.status == item["status"]
        assert attendance.crawled_at.replace(tzinfo=None) == item["crawled_at"]
        assert attendance.crawled_from == item["crawled_from"]

    def test_handle_with_changed_attendance_list(self):
        item = {
            "date": date(2020, 2, 3),
            "description": "Abertura da 1ª etapa do 4º período da 18ª legislatura",
            "council_member": "Roberto Luis da Silva Tourinho",
            "status": "ausente",
            "crawled_at": datetime(2020, 3, 21, 7, 15, 17, 276019),
            "crawled_from": "https://www.feiradesantana.ba.leg.br/lista/7/03-02-2020",
        }

        attendance = save_attendance_list(item)
        item["status"] = "falta_justificada"
        item["crawled_at"] = datetime(2020, 3, 22, 7, 15, 17, 908831)

        updated_attendance = save_attendance_list(item)

        assert attendance.pk == updated_attendance.pk
        assert attendance.council_member == updated_attendance.council_member
        assert attendance.description == updated_attendance.description
        assert attendance.crawled_from == updated_attendance.crawled_from
        assert attendance.status != updated_attendance.status
        assert attendance.crawled_at != updated_attendance.crawled_at


@pytest.mark.django_db
class TestSaveExpense:
    def test_save_expense(self):
        item = {
            "company_or_person": "G5 OPERADORA TURÍSTICA LTDA",
            "crawled_at": datetime(2020, 4, 10, 14, 0, 51, 43077),
            "crawled_from": "https://www.transparencia.feiradesantana.ba.leg.br/",
            "date": date(2019, 12, 23),
            "document": "12.627.959/0001-30",
            "function": "01 - LEGISLATIVA",
            "group": "Manutencao dos servicos tecnico administrativos",
            "legal_status": "339033010000 - Despesas com passagem Aérea         2002 - "
            "Manutencao dos servicos tecnico administrativos",
            "number": "01772-19",
            "phase": "pagamento",
            "process_number": "003/2017",
            "published_at": date(2019, 12, 23),
            "resource": "0000 - TESOURO",
            "subfunction": "031 - ACAO",
            "subgroup": "Despesas com passagem Aérea",
            "summary": "REF. A PASSAGENS AÉREAS SSA-FOR-THE/FORT-SSA PARA O VEREADOR "
            "ISAÍAS DOS SANTOS, EM VIAGEM A TERESINA/PI, NOS DIAS 08, 09 E "
            "10/2019, PARA VISITA AO PROJETO SASC INTEGRAÇÃO.",
            "type_of_process": "PREGAO",
            "value": 3414.03,
        }
        expense = save_expense(item)

        assert expense.company_or_person == item["company_or_person"]
        assert expense.crawled_at.replace(tzinfo=None) == item["crawled_at"]
        assert expense.crawled_from == item["crawled_from"]
        assert expense.date == item["date"]
        assert expense.document == item["document"]
        assert expense.function == item["function"]
        assert expense.group == item["group"]
        assert expense.legal_status == item["legal_status"]
        assert expense.number == item["number"]
        assert expense.phase == item["phase"]
        assert expense.process_number == item["process_number"]
        assert expense.published_at == item["published_at"]
        assert expense.resource == item["resource"]
        assert expense.subfunction == item["subfunction"]
        assert expense.subgroup == item["subgroup"]
        assert expense.summary == item["summary"]
        assert expense.type_of_process == item["type_of_process"]
        assert expense.value == item["value"]

    def test_save_expense_with_only_few_fields_filled(self):
        item = {
            "company_or_person": None,
            "crawled_at": datetime(2020, 4, 10, 14, 2, 26, 502801),
            "crawled_from": "https://www.transparencia.feiradesantana.ba.leg.br/",
            "date": date(2017, 3, 20),
            "document": None,
            "function": None,
            "legal_status": None,
            "number": "00228-17",
            "phase": "pagamento",
            "process_number": "",
            "published_at": date(2017, 3, 20),
            "resource": None,
            "subfunction": None,
            "summary": "REF. A OBRIGAÇÕES PATRONAIS SOBRE A FOLHA DE PAGAMENTO DOS "
            "FUNCIONÁRIOS CARGOS EM COMISSÃO DESTA CASA, COMPLEMENTO DO MÊS DE "
            "FEVEREIRO/2017.",
            "type_of_process": None,
            "value": 0.0,
            "subgroup": None,
            "group": None,
        }

        expense = save_expense(item)

        assert expense.crawled_at.replace(tzinfo=None) == item["crawled_at"]
        assert expense.crawled_from == item["crawled_from"]
        assert expense.company_or_person == item["company_or_person"]
        assert expense.date == item["date"]
        assert expense.document == item["document"]
        assert expense.function == item["function"]
        assert expense.group == item["group"]
        assert expense.legal_status == item["legal_status"]
        assert expense.number == item["number"]
        assert expense.phase == item["phase"]
        assert expense.process_number == item["process_number"]
        assert expense.published_at == item["published_at"]
        assert expense.resource == item["resource"]
        assert expense.subfunction == item["subfunction"]
        assert expense.subgroup == item["subgroup"]
        assert expense.summary == item["summary"]
        assert expense.type_of_process == item["type_of_process"]
        assert expense.value == item["value"]


@pytest.mark.django_db
class TestSaveMinute:
    def test_save_minute(self, mock_save_file):
        item = {
            "crawled_at": datetime(2020, 4, 30, 18, 18, 56, 173788),
            "crawled_from": "https://www.feiradesantana.ba.leg.br/atas?"
            "mes=9&ano=2018&Acessar=OK",
            "date": date(2018, 9, 11),
            "event_type": None,
            "file_content": "Casa da Cidadania",
            "file_urls": [
                "https://www.feiradesantana.ba.leg.br/admin/atas/5eaabb5e91088.pdf"
            ],
            "title": "Ata da 4ª Reunião para Instalação da Comissão Especial",
        }

        minute = save_minute(item)
        assert minute.date == item["date"]
        assert minute.title == item["title"]
        assert minute.event_type == item["event_type"]
        assert minute.crawled_from == item["crawled_from"]
