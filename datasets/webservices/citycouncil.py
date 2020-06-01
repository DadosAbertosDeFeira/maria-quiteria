from datetime import datetime

from datasets.models import CityCouncilBid
from datasets.parsers import (
    from_str_to_datetime,
    modality_mapping_from_city_council_db,
    to_boolean,
)
from datasets.webservices.adapters import CITYCOUNCIL_BID_FIELDS_MAPPING, map_to_fields
from django.conf import settings

FUNCTIONS = {
    "excluded": to_boolean,
    "session_at": from_str_to_datetime,
    "modality": modality_mapping_from_city_council_db,
}


def add_bid(record):
    new_item = map_to_fields(record, CITYCOUNCIL_BID_FIELDS_MAPPING, FUNCTIONS)
    new_item["crawled_at"] = datetime.now()
    new_item["crawled_from"] = settings.CITY_COUNCIL_WEBSERVICE_ENDPOINT
    return CityCouncilBid.objects.create(**new_item)


def bid_update(record):
    bid = CityCouncilBid.objects.get(external_code=record["codLic"])
    updated_item = map_to_fields(record, CITYCOUNCIL_BID_FIELDS_MAPPING, FUNCTIONS)
    for key, value in updated_item.items():
        setattr(bid, key, value)
    bid.save()
    return bid


def remove_bid(record):
    CityCouncilBid.objects.filter(external_code=record["codLic"]).update(excluded=True)
