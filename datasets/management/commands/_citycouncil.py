from datasets.models import CityCouncilAgenda, CityCouncilAttendanceList
from django.utils.timezone import make_aware


def save_agenda(item):
    agenda, _ = CityCouncilAgenda.objects.update_or_create(
        date=item["date"],
        title=item["title"],
        event_type=item["event_type"],
        crawled_from=item["crawled_from"],
        defaults={
            "crawled_at": make_aware(item["crawled_at"]),
            "details": item["details"],
        },
    )
    return agenda


def save_attendance_list(item):
    attendance, _ = CityCouncilAttendanceList.objects.update_or_create(
        date=item["date"],
        council_member=item["council_member"],
        defaults={
            "crawled_at": make_aware(item["crawled_at"]),
            "crawled_from": item["crawled_from"],
            "description": item["description"],
            "status": item.get("status"),
        },
    )
    return attendance
