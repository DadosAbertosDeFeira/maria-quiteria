from datasets.models import CityHallBid, CityHallBidEvent
from django.contrib.admin.options import get_content_type_for_model
from django.utils.timezone import make_aware

from ._file import save_file


def save_bid(item):
    file_url = item["file_urls"][0] if item.get("file_urls") else None  # FIXME remover
    bid, created = CityHallBid.objects.update_or_create(
        session_at=item["session_at"],
        public_agency=item["public_agency"],
        codes=item["codes"],
        defaults={
            "crawled_from": item["crawled_from"],
            "crawled_at": make_aware(item["crawled_at"]),
            "description": item["description"],
            "modality": item["modality"],
            "file_url": file_url,  # FIXME remover
            "file_content": item.get("file_content"),  # FIXME remover
        },
    )

    if created and item.get("file_urls"):
        content_type = get_content_type_for_model(bid)
        for file_url in item.get("file_urls"):
            # FIXME checksum
            save_file(file_url, content_type, bid.pk)

    content_type = get_content_type_for_model(CityHallBidEvent)
    for event in item["history"]:
        event_obj, created = CityHallBidEvent.objects.get_or_create(
            crawled_from=item["crawled_from"],
            bid=bid,
            published_at=event["published_at"],
            summary=event["event"],
            file_url=event.get("url"),  # FIXME remover
            defaults={"crawled_at": make_aware(item["crawled_at"])},
        )
        if created and event.get("url"):
            for file_url in event["url"]:
                # FIXME checksum
                save_file(file_url, content_type, event_obj.pk)
    return bid
