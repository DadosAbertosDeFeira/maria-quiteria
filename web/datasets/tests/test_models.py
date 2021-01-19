from datetime import date, datetime, timedelta

import pytest
from django.utils.timezone import make_aware
from model_bakery import baker

from web.datasets.models import (
    CityCouncilAgenda,
    CityCouncilAttendanceList,
    CityCouncilBid,
    CityCouncilContract,
    CityCouncilExpense,
    CityCouncilMinute,
    CityCouncilRevenue,
    CityHallBid,
    Gazette,
)


@pytest.mark.django_db
class TestCityCouncilAgenda:
    def test_return_none_for_last_collected_item_date_if_nothing_is_found(self):
        # não é salvo no banco - ou seja, banco vazio
        agenda = baker.prepare_recipe("datasets.CityCouncilAgenda")
        assert agenda.last_collected_item_date() is None

    def test_last_collected_item_date(self):
        expected_date = date(2020, 1, 1)  # início do ano
        agenda = baker.make_recipe("datasets.CityCouncilAgenda", date=date(2020, 2, 2))
        assert agenda.last_collected_item_date() == expected_date

    def test_default_order_should_be_respected(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe("datasets.CityCouncilAgenda", date=older_date)
        baker.make_recipe("datasets.CityCouncilAgenda", date=newer_date)
        agendas = CityCouncilAgenda.objects.all()
        assert agendas.first().date == newer_date
        assert agendas.last().date == older_date


@pytest.mark.django_db
class TestCityCouncilAttendanceList:
    def test_return_none_for_last_collected_item_date_if_nothing_is_found(self):
        # não é salvo no banco - ou seja, banco vazio
        attendance_list = baker.prepare_recipe("datasets.CityCouncilAttendanceList")
        assert attendance_list.last_collected_item_date() is None

    def test_last_collected_item_date(self):
        expected_date = date(2020, 1, 1)  # início do ano
        attendance_list = baker.make_recipe(
            "datasets.CityCouncilAttendanceList", date=date(2020, 2, 2)
        )
        assert attendance_list.last_collected_item_date() == expected_date

    def test_default_order_should_be_respected(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe("datasets.CityCouncilAttendanceList", date=older_date)
        baker.make_recipe("datasets.CityCouncilAttendanceList", date=newer_date)
        attendance_lists = CityCouncilAttendanceList.objects.all()
        assert attendance_lists.first().date == newer_date
        assert attendance_lists.last().date == older_date

    def test_save_should_create_historical_data(self):
        attendance_list = baker.make_recipe(
            "datasets.CityCouncilAttendanceList", status="presente"
        )
        assert attendance_list.history.count() == 1

        attendance_list.status = "falta_justificada"
        attendance_list.save()

        assert attendance_list.status == "falta_justificada"
        assert attendance_list.history.count() == 2
        assert attendance_list.history.earliest().status == "presente"

    def test_save_should_create_historical_data_bulk_save(self):
        attendance_lists = [
            baker.make_recipe("datasets.CityCouncilAttendanceList", status="presente")
            for _ in range(5)
        ]

        for attendance_list in attendance_lists:
            attendance_list.description = "foo bar"

        CityCouncilAttendanceList.objects.bulk_update(
            attendance_lists, fields=["description"]
        )

        for attendance_list in attendance_lists:
            attendance_list.history.count() == 2


@pytest.mark.django_db
class TestCityCouncilBid:
    def test_undated_should_be_shown_last(self):
        newer_datetime = make_aware(datetime(2020, 3, 18))
        older_datetime = make_aware(datetime(2020, 2, 3))
        baker.make_recipe("datasets.CityCouncilBid")
        baker.make_recipe("datasets.CityCouncilBid", session_at=older_datetime)
        baker.make_recipe("datasets.CityCouncilBid", session_at=newer_datetime)
        bids = CityCouncilBid.objects.all()
        assert bids.first().session_at == newer_datetime
        assert bids[1].session_at == older_datetime
        assert bids.last().session_at is None


@pytest.mark.django_db
class TestCityCouncilContract:
    def test_default_order_should_be_respected(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe("datasets.CityCouncilContract", start_date=older_date)
        baker.make_recipe("datasets.CityCouncilContract", start_date=newer_date)
        contracts = CityCouncilContract.objects.all()
        assert contracts.first().start_date == newer_date
        assert contracts.last().start_date == older_date


@pytest.mark.django_db
class TestCityCouncilExpense:
    def test_return_none_for_last_collected_item_date_if_nothing_is_found(self):
        # não é salvo no banco - ou seja, banco vazio
        expense = baker.prepare_recipe("datasets.CityCouncilExpense")
        assert expense.last_collected_item_date() is None

    def test_last_collected_item_date(self):
        expected_date = date(2019, 10, 1)
        expense = baker.make_recipe("datasets.CityCouncilExpense", date=expected_date)
        assert expense.last_collected_item_date() == expected_date

    def test_default_order_should_be_respected(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe("datasets.CityCouncilExpense", date=older_date)
        baker.make_recipe("datasets.CityCouncilExpense", date=newer_date)
        expenses = CityCouncilExpense.objects.all()
        assert expenses.first().date == newer_date
        assert expenses.last().date == older_date


@pytest.mark.django_db
class TestCityCouncilMinute:
    def test_return_none_for_last_collected_item_date_if_nothing_is_found(self):
        # não é salvo no banco - ou seja, banco vazio
        minute = baker.prepare_recipe("datasets.CityCouncilMinute")
        assert minute.last_collected_item_date() is None

    def test_last_collected_item_date(self):
        expected_date = date(2019, 10, 1)
        minute = baker.make_recipe("datasets.CityCouncilMinute", date=expected_date)
        assert minute.last_collected_item_date() == expected_date

    def test_default_order_should_be_respected(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe("datasets.CityCouncilMinute", date=older_date)
        baker.make_recipe("datasets.CityCouncilMinute", date=newer_date)
        minutes = CityCouncilMinute.objects.all()
        assert minutes.first().date == newer_date
        assert minutes.last().date == older_date


@pytest.mark.django_db
class TestCityCouncilRevenue:
    def test_undated_should_be_shown_last(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe("datasets.CityCouncilRevenue")
        baker.make_recipe("datasets.CityCouncilRevenue", published_at=older_date)
        baker.make_recipe("datasets.CityCouncilRevenue", published_at=newer_date)
        revenues = CityCouncilRevenue.objects.all()
        assert revenues.first().published_at == newer_date
        assert revenues[1].published_at == older_date
        assert revenues.last().published_at is None


@pytest.mark.django_db
class TestGazette:
    def test_return_none_for_last_collected_item_date_if_nothing_is_found(self):
        # não é salvo no banco - ou seja, banco vazio
        gazette = baker.prepare_recipe("datasets.Gazette")
        assert gazette.last_collected_item_date() is None

    def test_last_collected_item_date(self):
        expected_date = date(2019, 10, 1)
        gazette = baker.make_recipe("datasets.Gazette", date=expected_date)
        assert gazette.last_collected_item_date() == expected_date

    def test_undated_should_be_shown_last(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe("datasets.Gazette")
        baker.make_recipe("datasets.Gazette", date=older_date)
        baker.make_recipe("datasets.Gazette", date=newer_date)
        gazettes = Gazette.objects.all()
        assert gazettes.first().date == newer_date
        assert gazettes[1].date == older_date
        assert gazettes.last().date is None


@pytest.mark.django_db
class TestCityHallBid:
    def test_return_none_for_last_collected_item_date_if_nothing_is_found(self):
        bid = baker.prepare_recipe("datasets.CityHallBid")
        assert bid.last_collected_item_date() is None

    def test_last_collected_item_date_is_six_months_ago(self):
        expected_date = date.today() - timedelta(days=180)
        bid = baker.make_recipe("datasets.CityHallBid")
        assert bid.last_collected_item_date() == expected_date

    def test_undated_should_be_shown_last(self):
        newer_datetime = make_aware(datetime(2020, 3, 18))
        older_datetime = make_aware(datetime(2020, 2, 3))
        baker.make_recipe("datasets.CityHallBid")
        baker.make_recipe("datasets.CityHallBid", session_at=older_datetime)
        baker.make_recipe("datasets.CityHallBid", session_at=newer_datetime)
        bids = CityHallBid.objects.all()
        assert bids.first().session_at == newer_datetime
        assert bids[1].session_at == older_datetime
        assert bids.last().session_at is None
