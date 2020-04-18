from datasets.models import CityHallBid, CityHallBidEvent
from django.utils.timezone import make_aware


def save_bid(item):
    file_url = item["file_urls"][0] if item.get("file_urls") else None
    bid, _ = CityHallBid.objects.update_or_create(
        date=item["date"],
        category=item["category"],
        modality=item["modality"],
        defaults={
            "crawled_from": item["crawled_from"],
            "crawled_at": make_aware(item["crawled_at"]),
            "description": item["description"],
            "file_url": file_url,
            "file_content": item.get("file_content"),
        },
    )
    for event in item["history"]:
        CityHallBidEvent.objects.get_or_create(
            crawled_from=item["crawled_from"],
            bid=bid,
            date=event["date"],
            summary=event["event"],
            file_url=event.get("url"),
            defaults={"crawled_at": make_aware(item["crawled_at"])},
        )
    return bid
