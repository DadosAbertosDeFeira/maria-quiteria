import scrapy


class BaseItem(scrapy.Item):
    crawled_at = scrapy.Field()
    crawled_from = scrapy.Field()

    def __repr__(self):
        copy = self.deepcopy()
        if copy.get("file_content"):
            preview = copy["file_content"].strip()[:200]
            copy["file_content"] = f"Preview: {preview}"
        return super(BaseItem, copy).__repr__()


class LegacyGazetteItem(BaseItem):
    title = scrapy.Field()
    published_on = scrapy.Field()
    date = scrapy.Field()
    details = scrapy.Field()
    file_urls = scrapy.Field()
    file_content = scrapy.Field()


class GazetteEventItem(BaseItem):
    date = scrapy.Field()
    power = scrapy.Field()
    year_and_edition = scrapy.Field()
    event_title = scrapy.Field()
    event_secretariat = scrapy.Field()
    event_summary = scrapy.Field()
    file_urls = scrapy.Field()
    file_content = scrapy.Field()


class CityCouncilAgendaItem(BaseItem):
    date = scrapy.Field()
    details = scrapy.Field()
    title = scrapy.Field()
    event_type = scrapy.Field()


class CityHallContractItem(BaseItem):
    contract_id = scrapy.Field()
    starts_at = scrapy.Field()
    summary = scrapy.Field()
    contractor_document = scrapy.Field()  # CNPJ or CPF
    contractor_name = scrapy.Field()
    value = scrapy.Field()
    ends_at = scrapy.Field()
    file_urls = scrapy.Field()
    file_content = scrapy.Field()


class CityHallBidItem(BaseItem):
    category = scrapy.Field()
    month = scrapy.Field()
    year = scrapy.Field()
    description = scrapy.Field()
    history = scrapy.Field()
    modality = scrapy.Field()
    date = scrapy.Field()
    file_urls = scrapy.Field()
    file_content = scrapy.Field()


class CityHallPaymentsItem(BaseItem):
    published_at = scrapy.Field()
    phase = scrapy.Field()
    company_or_person = scrapy.Field()
    value = scrapy.Field()
    number = scrapy.Field()
    document = scrapy.Field()
    date = scrapy.Field()
    process_number = scrapy.Field()
    summary = scrapy.Field()
    group = scrapy.Field()
    action = scrapy.Field()
    function = scrapy.Field()
    subfunction = scrapy.Field()
    type_of_process = scrapy.Field()
    resource = scrapy.Field()


class EmployeeItem(BaseItem):
    agency = scrapy.Field()
    month = scrapy.Field()
    year = scrapy.Field()
    name = scrapy.Field()
    registration_number = scrapy.Field()
    condition = scrapy.Field()
    role = scrapy.Field()
    base_salary = scrapy.Field()
    benefits_salary = scrapy.Field()
    bonus_salary = scrapy.Field()
    workload = scrapy.Field()
    status = scrapy.Field()
    admission = scrapy.Field()
