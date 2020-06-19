from datetime import date, datetime, timedelta

import pytest
from datasets.models import (
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
from django.utils.timezone import make_aware
from model_bakery import baker


@pytest.mark.django_db
class TestCityCouncilAgenda:
    def test_return_none_for_last_collected_item_date_if_nothing_is_found(self):
        # não é salvo no banco - ou seja, banco vazio
        agenda = baker.prepare_recipe("datasets.CityCouncilAgenda")
        assert agenda.last_collected_item_date() is None

    def test_last_collected_item_date(self):
        expected_date = date(2020, 1, 1)  # início do ano
        agenda = baker.make_recipe("datasets.CityCouncilAgenda", date=date(2020, 2, 2),)
        assert agenda.last_collected_item_date() == expected_date

    def test_default_order_should_be_respected(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe(
            "datasets.CityCouncilAgenda", date=older_date,
        )
        baker.make_recipe(
            "datasets.CityCouncilAgenda", date=newer_date,
        )
        cc_agendas = CityCouncilAgenda.objects.all()
        assert cc_agendas.first().date == newer_date
        assert cc_agendas.last().date == older_date


@pytest.mark.django_db
class TestCityCouncilAttendanceList:
    def test_return_none_for_last_collected_item_date_if_nothing_is_found(self):
        # não é salvo no banco - ou seja, banco vazio
        attendance_list = baker.prepare_recipe("datasets.CityCouncilAttendanceList")
        assert attendance_list.last_collected_item_date() is None

    def test_last_collected_item_date(self):
        expected_date = date(2020, 1, 1)  # início do ano
        attendance_list = baker.make_recipe(
            "datasets.CityCouncilAttendanceList", date=date(2020, 2, 2),
        )
        assert attendance_list.last_collected_item_date() == expected_date

    def test_default_order_should_be_respected(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe(
            "datasets.CityCouncilAttendanceList", date=older_date,
        )
        baker.make_recipe(
            "datasets.CityCouncilAttendanceList", date=newer_date,
        )
        cc_attendance_lists = CityCouncilAttendanceList.objects.all()
        assert cc_attendance_lists.first().date == newer_date
        assert cc_attendance_lists.last().date == older_date


@pytest.mark.django_db
class TestCityCouncilBid:
    def test_undated_should_be_shown_last(self):
        newer_datetime = make_aware(datetime(2020, 3, 18))
        older_datetime = make_aware(datetime(2020, 2, 3))
        baker.make_recipe("datasets.CityCouncilBid")
        baker.make_recipe(
            "datasets.CityCouncilBid", session_at=older_datetime,
        )
        baker.make_recipe(
            "datasets.CityCouncilBid", session_at=newer_datetime,
        )
        cc_bids = CityCouncilBid.objects.all()
        assert cc_bids.first().session_at == newer_datetime
        assert cc_bids[1].session_at == older_datetime
        assert cc_bids.last().session_at is None


@pytest.mark.django_db
class TestCityCouncilContract:
    def test_default_order_should_be_respected(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe(
            "datasets.CityCouncilContract", start_date=older_date,
        )
        baker.make_recipe(
            "datasets.CityCouncilContract", start_date=newer_date,
        )
        cc_minutes = CityCouncilContract.objects.all()
        assert cc_minutes.first().start_date == newer_date
        assert cc_minutes.last().start_date == older_date


@pytest.mark.django_db
class TestCityCouncilExpense:
    def test_return_none_for_last_collected_item_date_if_nothing_is_found(self):
        # não é salvo no banco - ou seja, banco vazio
        expense = baker.prepare_recipe("datasets.CityCouncilExpense")
        assert expense.last_collected_item_date() is None

    def test_last_collected_item_date(self):
        expected_date = date(2019, 10, 1)
        expense = baker.make_recipe("datasets.CityCouncilExpense", date=expected_date,)
        assert expense.last_collected_item_date() == expected_date

    def test_default_order_should_be_respected(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe(
            "datasets.CityCouncilExpense", date=older_date,
        )
        baker.make_recipe(
            "datasets.CityCouncilExpense", date=newer_date,
        )
        cc_expenses = CityCouncilExpense.objects.all()
        assert cc_expenses.first().date == newer_date
        assert cc_expenses.last().date == older_date


@pytest.mark.django_db
class TestCityCouncilMinute:
    def test_return_none_for_last_collected_item_date_if_nothing_is_found(self):
        # não é salvo no banco - ou seja, banco vazio
        minute = baker.prepare_recipe("datasets.CityCouncilMinute")
        assert minute.last_collected_item_date() is None

    def test_last_collected_item_date(self):
        expected_date = date(2019, 10, 1)
        minute = baker.make_recipe("datasets.CityCouncilMinute", date=expected_date,)
        assert minute.last_collected_item_date() == expected_date

    def test_default_order_should_be_respected(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe(
            "datasets.CityCouncilMinute", date=older_date,
        )
        baker.make_recipe(
            "datasets.CityCouncilMinute", date=newer_date,
        )
        cc_minutes = CityCouncilMinute.objects.all()
        assert cc_minutes.first().date == newer_date
        assert cc_minutes.last().date == older_date


@pytest.mark.django_db
class TestCityCouncilRevenue:
    def test_undated_should_be_shown_last(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe("datasets.CityCouncilRevenue")
        baker.make_recipe(
            "datasets.CityCouncilRevenue", published_at=older_date,
        )
        baker.make_recipe(
            "datasets.CityCouncilRevenue", published_at=newer_date,
        )
        cc_revenues = CityCouncilRevenue.objects.all()
        assert cc_revenues.first().published_at == newer_date
        assert cc_revenues[1].published_at == older_date
        assert cc_revenues.last().published_at is None


@pytest.mark.django_db
class TestGazette:
    def test_return_none_for_last_collected_item_date_if_nothing_is_found(self):
        # não é salvo no banco - ou seja, banco vazio
        gazette = baker.prepare_recipe("datasets.Gazette")
        assert gazette.last_collected_item_date() is None

    def test_last_collected_item_date(self):
        expected_date = date(2019, 10, 1)
        gazette = baker.make_recipe("datasets.Gazette", date=expected_date,)
        assert gazette.last_collected_item_date() == expected_date

    def test_undated_should_be_shown_last(self):
        newer_date = date(2020, 3, 18)
        older_date = date(2020, 2, 3)
        baker.make_recipe("datasets.Gazette")
        baker.make_recipe(
            "datasets.Gazette", date=older_date,
        )
        baker.make_recipe(
            "datasets.Gazette", date=newer_date,
        )
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
        baker.make_recipe(
            "datasets.CityHallBid", session_at=older_datetime,
        )
        baker.make_recipe(
            "datasets.CityHallBid", session_at=newer_datetime,
        )
        ch_bids = CityHallBid.objects.all()
        assert ch_bids.first().session_at == newer_datetime
        assert ch_bids[1].session_at == older_datetime
        assert ch_bids.last().session_at is None
