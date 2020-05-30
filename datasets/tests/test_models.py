from datetime import date, timedelta

import pytest
from datasets.models import Paycheck
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


@pytest.mark.django_db
class TestCityHallBid:
    def test_return_none_for_last_collected_item_date_if_nothing_is_found(self):
        bid = baker.prepare_recipe("datasets.CityHallBid")
        assert bid.last_collected_item_date() is None

    def test_last_collected_item_date_is_six_months_ago(self):
        expected_date = date.today() - timedelta(days=180)
        bid = baker.make_recipe("datasets.CityHallBid")
        assert bid.last_collected_item_date() == expected_date


class TestPaycheck:
    @pytest.mark.django_db
    def test_show_when_last_collected_item(self):
        newest_paycheck = baker.make("datasets.Paycheck", month=1, year=2020)
        baker.make("datasets.Paycheck", month=10, year=2000)
        baker.make("datasets.Paycheck", month=1, year=2019)

        assert (
            Paycheck.last_collected_item_date()
            == newest_paycheck.last_collected_item_date()
        )

    @pytest.mark.django_db
    def test_return_none_when_any_paychecks_were_collected(self):
        assert Paycheck.last_collected_item_date() is None
