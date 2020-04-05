from datasets.models import CityHallBid, CityHallBidEvent
from django.utils.timezone import make_aware


def save_bid(item):
    file_url = item["file_urls"][0] if item.get("file_urls") else None
    bid = CityHallBid.objects.create(
        crawled_from=item["crawled_from"],
        crawled_at=make_aware(item["crawled_at"]),
        date=item["date"],
        category=item["category"],
        description=item["description"],
        modality=item["modality"],
        file_url=file_url,
        file_content=item.get("file_content"),
    )
    for event in item["history"]:
        file_url = event["file_urls"][0] if event.get("file_urls") else None
        CityHallBidEvent.objects.create(
            crawled_from=item["crawled_from"],
            crawled_at=make_aware(item["crawled_at"]),
            bid=bid,
            date=event["date"],
            summary=event["event"],
            file_url=file_url,
            file_content=event.get("file_content"),
        )
    return bid
