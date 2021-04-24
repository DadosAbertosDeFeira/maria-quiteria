from datetime import date, datetime

import pytest
from web.datasets.parsers import (
    currency_to_float,
    from_str_to_date,
    from_str_to_datetime,
)


@pytest.mark.parametrize(
    "original_value,expected_value",
    [
        ("R$ 69.848,70", 69848.70),
        ("69.848,70", 69848.70),
        ("R$ -69.848,70", -69848.70),
        ("1,70", 1.70),
        ("00,00", 0),
        ("Random", None),
        ("37500.36", 37500.36),
        ("'37500.36", 37500.36),
        ("R$ 37.500,36", 37500.36),
    ],
)
def test_currency_to_float(original_value, expected_value):
    assert currency_to_float(original_value) == expected_value


@pytest.mark.parametrize(
    "datetime_str,expected_obj",
    [
        ("26/02/2020 19:28", datetime(2020, 2, 26, 19, 28)),
        ("26/2/2014 09:00", datetime(2014, 2, 26, 9, 0)),
        ("26/02/2020 19:28:00", None),
        ("26/02/2020", None),
        ("26.02.20", None),
        (None, None),
        ("", None),
    ],
)
def test_possible_datetime_formats(datetime_str, expected_obj):
    formats = ["%d/%m/%Y %H:%M"]

    assert from_str_to_datetime(datetime_str, formats) == expected_obj


@pytest.mark.parametrize(
    "datetime_str,expected_obj",
    [
        ("26/02/20", datetime(2020, 2, 26)),
        ("26/02/2020", datetime(2020, 2, 26)),
        ("26/2/2020", datetime(2020, 2, 26)),
        ("26/02/2020 19:28", None),
        ("26.02.20", None),
        (None, None),
        ("", None),
    ],
)
def test_possible_date_formats(datetime_str, expected_obj):
    formats = ["%d/%m/%Y", "%d/%m/%y"]

    assert from_str_to_datetime(datetime_str, formats) == expected_obj


@pytest.mark.parametrize(
    "datetime_str,expected_obj",
    [
        ("26/02/2020 19:28", datetime(2020, 2, 26, 19, 28)),
        ("26/2/2014 09:00", datetime(2014, 2, 26, 9, 0)),
        ("26/02/2020 19:28:00", datetime(2020, 2, 26, 19, 28, 0)),
        ("26/02/2020", None),
        ("26.02.20", None),
        (None, None),
        ("", None),
    ],
)
def test_possible_datetime(datetime_str, expected_obj):
    assert from_str_to_datetime(datetime_str) == expected_obj


@pytest.mark.parametrize(
    "date_str,expected_obj",
    [
        ("26/02/2020 19:28", None),
        ("26/2/2014 09:00", None),
        ("26/02/2020 19:28:00", None),
        ("26/02/2020", date(2020, 2, 26)),
        ("26/02/20", date(2020, 2, 26)),
        ("26.02.20", None),
        (None, None),
        ("", None),
    ],
)
def test_possible_date(date_str, expected_obj):
    assert from_str_to_date(date_str) == expected_obj


@pytest.mark.parametrize(
    "datetime_str,expected_obj",
    [
        ("18/05/2020", datetime(2020, 5, 18)),
        ("18/09/1833", datetime(1833, 9, 18)),
        ("17/09/1833", None),
        ("01/01/0001", None),
    ],
)
def test_dates_older_than_city_creation(datetime_str, expected_obj):
    formats = ["%d/%m/%Y", "%d/%m/%y"]

    assert from_str_to_datetime(datetime_str, formats) == expected_obj
