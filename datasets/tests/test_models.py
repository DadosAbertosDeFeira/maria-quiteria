import pytest
from datasets.models import Employee
from model_bakery import baker


class TestEmployee:
    @pytest.mark.django_db
    def test_show_when_last_collect_was_performed(self):
        baker.make("datasets.Employee")
        baker.make("datasets.Employee")
        last_record = baker.make("datasets.Employee")

        assert Employee.last_collected_item_date() == last_record.crawled_at.date()

    @pytest.mark.django_db
    def test_return_none_when_no_employees_were_collected(self):
        assert Employee.last_collected_item_date() is None
