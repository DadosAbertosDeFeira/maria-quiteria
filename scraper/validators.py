from schematics.models import Model
from schematics.types import (
    DateTimeType,
    DateType,
    DictType,
    FloatType,
    IntType,
    ListType,
    StringType,
    URLType,
)


class BaseModel(Model):
    crawled_at = DateTimeType(required=True)
    crawled_from = URLType(required=True)


class LegacyGazetteItem(BaseModel):
    title = StringType(required=True)
    published_on = StringType(required=False)
    # important info but not available in years like 2010
    date = DateType(required=False)
    details = StringType(required=True)
    file_urls = ListType(StringType)
    file_content = StringType()


class GazetteItem(BaseModel):
    date = DateType()
    power = StringType(required=True)
    year_and_edition = StringType(required=True)
    events = ListType(DictType(StringType), required=True)
    file_urls = ListType(StringType, required=True)
    file_content = StringType()


class CityCouncilAgendaItem(BaseModel):
    date = DateType()
    details = StringType()
    title = StringType(required=True)
    event_type = StringType(required=True)


class CityCouncilAttendanceListItem(BaseModel):
    date = DateType()
    description = StringType()
    council_member = StringType(required=True)
    status = StringType(required=True)


class CityCouncilExpenseItem(BaseModel):
    published_date = DateType()
    phase = StringType()
    company_or_person = StringType()
    value = FloatType()
    number = StringType()
    document = StringType()
    date = DateType()
    process_number = StringType()
    summary = StringType()
    legal_status = StringType()
    function = StringType()
    subfunction = StringType()
    type_of_process = StringType()
    resource = StringType()
    subgroup = StringType()
    group = StringType()


class CityCouncilMinuteItem(BaseModel):
    date = DateType()
    title = StringType(required=True)
    event_type = StringType(required=True)
    file_urls = ListType(StringType, required=True)
    file_content = StringType()


class CityHallContractItem(BaseModel):
    contract_id = StringType(required=True)
    starts_at = DateType(formats=("%d/%m/%Y", "%d/%m/%y"))
    summary = StringType()
    contractor_document = StringType()
    contractor_name = StringType()
    value = StringType()
    ends_at = DateType(formats=("%d/%m/%Y", "%d/%m/%y"))
    file_urls = ListType(StringType)
    file_content = StringType()


class CityHallBidItem(BaseModel):
    public_agency = StringType()
    month = IntType(min_value=1, max_value=12)
    year = IntType(min_value=1873)  # quando Feira virou cidade :)
    description = StringType()
    history = ListType(DictType(StringType))
    codes = StringType()
    modality = StringType()
    session_at = DateTimeType()
    file_urls = ListType(StringType)
    file_content = StringType()


class CityHallPaymentsItem(BaseModel):
    published_at = DateType(formats=("%d/%m/%Y", "%d/%m/%y"))
    phase = StringType()
    company_or_person = StringType(required=True)
    value = StringType(required=True)
    number = StringType()
    document = StringType(required=True)
    date = DateType(formats=("%d/%m/%Y", "%d/%m/%y"))
    process_number = StringType()
    summary = StringType()
    group = StringType()
    action = StringType()
    function = StringType()
    subfunction = StringType()
    type_of_process = StringType()
    resource = StringType()
