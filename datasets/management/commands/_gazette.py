import re
from datetime import date

from datasets.models import Gazette, GazetteEvent
from django.contrib.admin.options import get_content_type_for_model
from django.utils.timezone import make_aware

from ._file import save_file


def save_gazette(item):
    """Salva diários oficiais do executivo a partir de 2015."""
    gazette, created = Gazette.objects.update_or_create(
        date=item["date"],
        power=item["power"],
        year_and_edition=item["year_and_edition"],
        defaults={
            "crawled_at": make_aware(item["crawled_at"]),
            "crawled_from": item["crawled_from"],
            "file_url": item["file_urls"][0],
        },
    )

    if created:
        content_type = get_content_type_for_model(gazette)
        for file_url in item["file_urls"]:
            # FIXME checksum
            save_file(file_url, content_type, gazette.pk)

    for event in item["events"]:
        GazetteEvent.objects.get_or_create(
            gazette=gazette,
            title=event["title"],
            secretariat=event["secretariat"],
            crawled_from=item["crawled_from"],
            summary=event["summary"],
            defaults={"crawled_at": make_aware(item["crawled_at"])},
        )
    return gazette


def save_legacy_gazette(item):
    """Salva diários oficiais do executivo de antes de 2015.

    Os diários oficiais eram publicados em um site diferente do atual e
    também em jornais. Além disso, tinham um formato diferente, sendo um
    arquivo para cada evento (decreto, leis etc).
    Alguns não possuem data (especialmente os do ano de 2010). Por isso a
    tentativa de extrair a data do título.
    """

    notes = ""
    if item["date"] is None:
        extracted_date = _extract_date(item["title"])
        if extracted_date:
            item["date"] = extracted_date
            notes = "Data extraída do título."

    gazette, created = Gazette.objects.get_or_create(
        date=item["date"],
        power="executivo",
        crawled_from=item["crawled_from"],
        is_legacy=True,
        defaults={"crawled_at": make_aware(item["crawled_at"]), "notes": notes},
    )

    if created:
        content_type = get_content_type_for_model(gazette)
        for file_url in item["file_urls"]:
            # FIXME checksum
            save_file(file_url, content_type, gazette.pk)

    GazetteEvent.objects.create(
        gazette=gazette,
        title=item["title"],
        crawled_from=item["crawled_from"],
        summary=item["details"],
        published_on=item["published_on"],
        crawled_at=make_aware(item["crawled_at"]),
    )
    return gazette


def _extract_date(str_date):
    if str_date is None:
        return
    pattern = r"(\d+) DE (\w+) DE (\d{4})"
    result = re.search(pattern, str_date, re.IGNORECASE)
    if result:
        months = {
            "janeiro": 1,
            "fevereiro": 2,
            "março": 3,
            "marco": 3,
            "abril": 4,
            "maio": 5,
            "junho": 6,
            "julho": 7,
            "agosto": 8,
            "setembro": 9,
            "outubro": 10,
            "novembro": 11,
            "dezembro": 12,
        }
        day = int(result.group(1))
        month = result.group(2).lower()
        year = int(result.group(3))
        return date(year, months[month], day)
    return result
