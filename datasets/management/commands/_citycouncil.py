from datasets.management.commands._file import save_file
from datasets.models import (
    CityCouncilAgenda,
    CityCouncilAttendanceList,
    CityCouncilExpense,
    CityCouncilMinute,
)
from django.contrib.admin.options import get_content_type_for_model


def save_agenda(item):
    agenda, _ = CityCouncilAgenda.objects.update_or_create(
        date=item["date"],
        title=item["title"],
        event_type=item["event_type"],
        crawled_from=item["crawled_from"],
        defaults={"crawled_at": item["crawled_at"], "details": item["details"]},
    )
    return agenda


def save_attendance_list(item):
    attendance, _ = CityCouncilAttendanceList.objects.update_or_create(
        date=item["date"],
        council_member=item["council_member"],
        defaults={
            "crawled_at": item["crawled_at"],
            "crawled_from": item["crawled_from"],
            "description": item["description"],
            "status": item.get("status"),
        },
    )
    return attendance


def save_expense(item):
    attendance, _ = CityCouncilExpense.objects.get_or_create(
        published_at=item["published_at"],
        phase=item["phase"],
        company_or_person=item["company_or_person"],
        value=item["value"],
        number=item["number"],
        document=item["document"],
        date=item["date"],
        process_number=item["process_number"],
        summary=item["summary"],
        legal_status=item["legal_status"],
        function=item["function"],
        subfunction=item["subfunction"],
        type_of_process=item["type_of_process"],
        resource=item["resource"],
        subgroup=item["subgroup"],
        group=item["group"],
        defaults={
            "crawled_at": item["crawled_at"],
            "crawled_from": item["crawled_from"],
        },
    )
    return attendance


def save_minute(item):
    minute, created = CityCouncilMinute.objects.get_or_create(
        date=item["date"],
        crawled_from=item["crawled_from"],
        defaults={
            "title": item["title"],
            "event_type": item["event_type"],
            "crawled_at": item["crawled_at"],
        },
    )
    if created and item.get("files"):
        content_type = get_content_type_for_model(minute)
        for file_ in item["files"]:
            save_file(file_, content_type, minute.pk)
    return minute
