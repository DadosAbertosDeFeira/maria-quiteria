from datetime import datetime

from datasets.models import CityCouncilBid, CityCouncilContract
from datasets.webservices.adapters import (
    CITYCOUNCIL_BID_FIELDS_MAPPING,
    CITYCOUNCIL_BID_FUNCTIONS,
    CITYCOUNCIL_CONTRACT_FIELDS_MAPPING,
    CITYCOUNCIL_CONTRACT_FUNCTIONS,
    map_to_fields,
)
from django.conf import settings


def add_bid(record):
    new_item = map_to_fields(
        record, CITYCOUNCIL_BID_FIELDS_MAPPING, CITYCOUNCIL_BID_FUNCTIONS
    )
    new_item["crawled_at"] = datetime.now()
    new_item["crawled_from"] = settings.CITY_COUNCIL_WEBSERVICE_ENDPOINT
    return CityCouncilBid.objects.create(**new_item)


def bid_update(record):
    bid = CityCouncilBid.objects.get(external_code=record["codLic"])
    updated_item = map_to_fields(
        record, CITYCOUNCIL_BID_FIELDS_MAPPING, CITYCOUNCIL_BID_FUNCTIONS
    )
    for key, value in updated_item.items():
        setattr(bid, key, value)
    bid.save()
    return bid


def remove_bid(record):
    CityCouncilBid.objects.filter(external_code=record["codLic"]).update(excluded=True)


def add_contract(record):
    new_item = map_to_fields(
        record, CITYCOUNCIL_CONTRACT_FIELDS_MAPPING, CITYCOUNCIL_CONTRACT_FUNCTIONS
    )
    new_item["crawled_at"] = datetime.now()
    new_item["crawled_from"] = settings.CITY_COUNCIL_WEBSERVICE_ENDPOINT
    return CityCouncilContract.objects.create(**new_item)


def update_contract(record):
    contract = CityCouncilContract.objects.get(external_code=record["codCon"])
    updated_item = map_to_fields(
        record, CITYCOUNCIL_CONTRACT_FIELDS_MAPPING, CITYCOUNCIL_CONTRACT_FUNCTIONS
    )
    for key, value in updated_item.items():
        setattr(contract, key, value)
    contract.save()
    return contract


def remove_contract(record):
    CityCouncilContract.objects.filter(external_code=record["codCon"]).update(
        excluded=True
    )
