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
    date = DateType(required=False, formats=("%d/%m/%Y", "%d/%m/%y"))
    details = StringType(required=True)
    file_urls = ListType(URLType)
    file_content = StringType()


class GazetteEventItem(BaseModel):
    date = DateType(formats=("%d/%m/%Y", "%d/%m/%y"))
    power = StringType(required=True)
    year_and_edition = StringType(required=True)
    event_title = StringType(required=True)
    event_secretariat = StringType(required=True)
    event_summary = StringType(required=True)
    file_urls = ListType(URLType)
    file_content = StringType()


class CityCouncilAgendaItem(BaseModel):
    date = DateType(formats=("%d/%m/%Y", "%d/%m/%y"))
    details = StringType()
    title = StringType(required=True)
    event_type = StringType(required=True)


class CityHallContractItem(BaseModel):
    contract_id = StringType(required=True)
    starts_at = DateType(formats=("%d/%m/%Y", "%d/%m/%y"))
    summary = StringType()
    contractor_document = StringType()
    contractor_name = StringType()
    value = StringType()
    ends_at = DateType(formats=("%d/%m/%Y", "%d/%m/%y"))
    file_urls = ListType(StringType)  # TODO check URL type
    file_content = StringType()


class CityHallBidItem(BaseModel):
    category = StringType()
    month = IntType(min_value=1, max_value=12)
    year = IntType(min_value=1873)  # quando Feira virou cidade :)
    description = StringType()
    history = ListType(DictType(StringType))
    modality = StringType()
    date = DateTimeType(formats=("%d/%m/%Y %Hh%M"))
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


class EmployeeItem(BaseModel):
    agency = StringType(required=True)
    month = IntType(required=True)
    year = IntType(required=True)
    name = StringType(required=True)
    registration_number = StringType(required=True)
    condition = StringType()
    role = StringType()
    base_salary = FloatType(required=True)
    benefits_salary = FloatType()
    bonus_salary = FloatType()
    workload = IntType()
    status = StringType()
    admission = DateType()
