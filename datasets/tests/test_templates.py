from datetime import date, datetime

import pytest
from django.utils.timezone import make_aware
from model_bakery import baker


@pytest.mark.django_db
class TestCityCouncilAgenda:
    def test_default_order_should_be_respected(self, client):
        older = baker.make_recipe(
            "datasets.CityCouncilAgenda",
            date=date(2020, 2, 3),
            title="older_cc_agenda",
        )
        newer = baker.make_recipe(
            "datasets.CityCouncilAgenda",
            date=date(2020, 3, 18),
            title="newer_cc_agenda",
        )
        content = str(
            client.get("/painel/datasets/citycouncilagenda/").content.decode("utf-8")
        )
        pos_newer = content.find(newer.title)
        pos_older = content.find(older.title)
        assert pos_newer < pos_older


@pytest.mark.django_db
class TestCityCouncilAttendanceList:
    def test_default_order_should_be_respected(self, client):
        older = baker.make_recipe(
            "datasets.CityCouncilAttendanceList",
            date=date(2020, 2, 3),
            description="older_cc_attendance_list",
        )
        newer = baker.make_recipe(
            "datasets.CityCouncilAttendanceList",
            date=date(2020, 3, 18),
            description="newer_cc_attendance_list",
        )
        content = str(
            client.get("/painel/datasets/citycouncilattendancelist/").content.decode(
                "utf-8"
            )
        )
        pos_newer = content.find(newer.description)
        pos_older = content.find(older.description)
        assert pos_newer < pos_older


@pytest.mark.django_db
class TestCityCouncilBid:
    def test_undated_should_be_show_last(self, client):
        older = baker.make_recipe(
            "datasets.CityCouncilBid",
            session_at=make_aware(datetime(2020, 2, 3)),
            description="older_cc_bid",
        )
        undated = baker.make_recipe(
            "datasets.CityCouncilBid", description="undated_cc_bid",
        )
        newer = baker.make_recipe(
            "datasets.CityCouncilBid",
            session_at=make_aware(datetime(2020, 3, 18)),
            description="newer_cc_bid",
        )
        content = str(
            client.get("/painel/datasets/citycouncilbid/").content.decode("utf-8")
        )
        pos_newer = content.find(newer.description)
        pos_older = content.find(older.description)
        pos_undated = content.find(undated.description)
        assert pos_newer < pos_older < pos_undated


@pytest.mark.django_db
class TestCityCouncilContract:
    def test_default_order_should_be_respected(self, client):
        older = baker.make_recipe(
            "datasets.CityCouncilContract",
            start_date=date(2020, 2, 3),
            description="older_cc_contract",
        )
        newer = baker.make_recipe(
            "datasets.CityCouncilContract",
            start_date=date(2020, 3, 18),
            description="newer_cc_contract",
        )
        content = str(
            client.get("/painel/datasets/citycouncilcontract/").content.decode("utf-8")
        )
        pos_newer = content.find(newer.description)
        pos_older = content.find(older.description)
        assert pos_newer < pos_older


@pytest.mark.django_db
class TestCityCouncilExpense:
    def test_default_order_should_be_respected(self, client):
        older = baker.make_recipe(
            "datasets.CityCouncilExpense",
            date=date(2020, 2, 3),
            summary="older_cc_expense",
        )
        newer = baker.make_recipe(
            "datasets.CityCouncilExpense",
            date=date(2020, 3, 18),
            summary="newer_cc_expense",
        )
        content = str(
            client.get("/painel/datasets/citycouncilexpense/").content.decode("utf-8")
        )
        pos_newer = content.find(newer.summary)
        pos_older = content.find(older.summary)
        assert pos_newer < pos_older


@pytest.mark.django_db
class TestCityCouncilMinute:
    def test_default_order_should_be_respected(self, client):
        older = baker.make_recipe(
            "datasets.CityCouncilMinute",
            date=date(2020, 2, 3),
            title="older_cc_minute",
        )
        newer = baker.make_recipe(
            "datasets.CityCouncilMinute",
            date=date(2020, 3, 18),
            title="newer_cc_minute",
        )
        content = str(
            client.get("/painel/datasets/citycouncilminute/").content.decode("utf-8")
        )
        pos_newer = content.find(newer.title)
        pos_older = content.find(older.title)
        assert pos_newer < pos_older


@pytest.mark.django_db
class TestCityCouncilRevenue:
    def test_undated_should_be_show_last(self, client):
        older = baker.make_recipe(
            "datasets.CityCouncilRevenue",
            published_at=date(2020, 2, 3),
            description="older_cc_revenue",
        )
        undated = baker.make_recipe(
            "datasets.CityCouncilRevenue", description="undated_cc_revenue",
        )
        newer = baker.make_recipe(
            "datasets.CityCouncilRevenue",
            published_at=date(2020, 3, 18),
            description="newer_cc_revenue",
        )
        content = str(
            client.get("/painel/datasets/citycouncilrevenue/").content.decode("utf-8")
        )
        pos_newer = content.find(newer.description)
        pos_older = content.find(older.description)
        pos_undated = content.find(undated.description)
        assert pos_newer < pos_older < pos_undated


@pytest.mark.django_db
class TestCityHallBid:
    def test_undated_should_be_show_last(self, client):
        older = baker.make_recipe(
            "datasets.CityHallBid",
            session_at=make_aware(datetime(2020, 2, 3)),
            description="older_ch_bid",
        )
        undated = baker.make_recipe(
            "datasets.CityHallBid", description="undated_ch_bid",
        )
        newer = baker.make_recipe(
            "datasets.CityHallBid",
            session_at=make_aware(datetime(2020, 3, 18)),
            description="newer_ch_bid",
        )
        content = str(
            client.get("/painel/datasets/cityhallbid/").content.decode("utf-8")
        )
        pos_newer = content.find(newer.description)
        pos_older = content.find(older.description)
        pos_undated = content.find(undated.description)
        assert pos_newer < pos_older < pos_undated


@pytest.mark.django_db
class TestGazette:
    def test_undated_should_be_shown_last(self, client):
        older = baker.make_recipe("datasets.Gazette", date=date(2020, 2, 3),)
        undated = baker.make_recipe("datasets.Gazette")
        newer = baker.make_recipe("datasets.Gazette", date=date(2020, 3, 18),)
        content = str(client.get("/painel/datasets/gazette/").content.decode("utf-8"))
        pos_newer = content.find(newer.year_and_edition)
        pos_older = content.find(older.year_and_edition)
        pos_undated = content.find(undated.year_and_edition)
        assert pos_newer < pos_older < pos_undated
