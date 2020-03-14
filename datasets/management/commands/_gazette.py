from datasets.models import Gazette, GazetteEvent
from django.utils.timezone import make_aware


def save_gazette(item):
    gazette, _ = Gazette.objects.update_or_create(
        date=item["date"],
        power=item["power"],
        year_and_edition=item["year_and_edition"],
        defaults={
            "crawled_at": make_aware(item["crawled_at"]),
            "crawled_from": item["crawled_from"],
            "file_urls": item["file_urls"],
            "file_content": item.get("file_content"),
        },
    )
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
