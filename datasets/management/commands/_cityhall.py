from datasets.models import CityHallBid
from django.utils.timezone import make_aware


def save_bid(item):
    file_url = item["file_urls"][0] if item.get("file_urls") else None
    return CityHallBid.objects.create(
        crawled_from=item["crawled_from"],
        crawled_at=make_aware(item["crawled_at"]),
        date=item["date"],
        category=item["category"],
        description=item["description"],
        modality=item["modality"],
        file_url=file_url,
        file_content=item.get("file_content"),
    )
