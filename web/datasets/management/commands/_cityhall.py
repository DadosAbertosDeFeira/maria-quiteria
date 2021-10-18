from django.contrib.admin.options import get_content_type_for_model

from web.datasets.models import CityHallBid, CityHallBidEvent

from ._file import save_file


def save_bid(item):
    bid, created = CityHallBid.objects.update_or_create(
        session_at=item["session_at"],
        public_agency=item["public_agency"],
        codes=item["codes"],
        defaults={
            "crawled_from": item["crawled_from"],
            "crawled_at": item["crawled_at"],
            "description": item["description"],
            "modality": item["modality"],
        },
    )

    if created and item.get("files"):
        content_type = get_content_type_for_model(bid)
        for file_ in item["files"]:
            save_file(file_, content_type, bid.pk)

    content_type = get_content_type_for_model(CityHallBidEvent)
    for event in item["history"]:
        event_obj, created = CityHallBidEvent.objects.get_or_create(
            crawled_from=item["crawled_from"],
            bid=bid,
            published_at=event["published_at"],
            summary=event["event"],
            defaults={"crawled_at": item["crawled_at"]},
        )
        if created and event.get("url"):
            save_file(event.get("url"), content_type, event_obj.pk)
    return bid
