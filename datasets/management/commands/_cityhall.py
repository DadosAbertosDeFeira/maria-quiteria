from datasets.models import CityHallBid, CityHallBidEvent
from django.utils.timezone import make_aware


def save_bid(item):
    file_url = item["file_urls"][0] if item.get("file_urls") else None
    bid, _ = CityHallBid.objects.update_or_create(
        session_at=item["session_at"],
        public_agency=item["public_agency"],
        codes=item["codes"],
        defaults={
            "crawled_from": item["crawled_from"],
            "crawled_at": make_aware(item["crawled_at"]),
            "description": item["description"],
            "modality": item["modality"],
            "file_url": file_url,
            "file_content": item.get("file_content"),
        },
    )
    for event in item["history"]:
        CityHallBidEvent.objects.get_or_create(
            crawled_from=item["crawled_from"],
            bid=bid,
            published_at=event["published_at"],
            summary=event["event"],
            file_url=event.get("url"),
            defaults={"crawled_at": make_aware(item["crawled_at"])},
        )
    return bid
