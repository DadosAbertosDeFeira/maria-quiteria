import scrapy


class BaseItem(scrapy.Item):
    crawled_at = scrapy.Field()
    crawled_from = scrapy.Field()

    def __repr__(self):
        copy = self.deepcopy()
        if copy.get("files"):
            for file_ in copy["files"]:
                if file_["content"]:
                    preview = file_["content"].strip()[:200]
                    file_["content"] = f"Preview: {preview}"
        return super(BaseItem, copy).__repr__()


class LegacyGazetteItem(BaseItem):
    title = scrapy.Field()
    published_on = scrapy.Field()
    date = scrapy.Field()
    details = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()


class GazetteItem(BaseItem):
    date = scrapy.Field()
    power = scrapy.Field()
    year_and_edition = scrapy.Field()
    events = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()


class CityCouncilAgendaItem(BaseItem):
    date = scrapy.Field()
    details = scrapy.Field()
    title = scrapy.Field()
    event_type = scrapy.Field()


class CityCouncilAttendanceListItem(BaseItem):
    date = scrapy.Field()
    description = scrapy.Field()
    council_member = scrapy.Field()
    status = scrapy.Field()


class CityCouncilExpenseItem(BaseItem):
    published_at = scrapy.Field()
    phase = scrapy.Field()
    company_or_person = scrapy.Field()
    value = scrapy.Field()
    number = scrapy.Field()
    document = scrapy.Field()
    date = scrapy.Field()
    process_number = scrapy.Field()
    summary = scrapy.Field()
    legal_status = scrapy.Field()
    function = scrapy.Field()
    subfunction = scrapy.Field()
    type_of_process = scrapy.Field()
    resource = scrapy.Field()
    subgroup = scrapy.Field()
    group = scrapy.Field()


class CityCouncilMinuteItem(BaseItem):
    date = scrapy.Field()
    title = scrapy.Field()
    event_type = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()


class CityHallContractItem(BaseItem):
    contract_id = scrapy.Field()
    starts_at = scrapy.Field()
    summary = scrapy.Field()
    contractor_document = scrapy.Field()  # CNPJ or CPF
    contractor_name = scrapy.Field()
    value = scrapy.Field()
    ends_at = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()


class CityHallBidItem(BaseItem):
    public_agency = scrapy.Field()
    month = scrapy.Field()
    year = scrapy.Field()
    description = scrapy.Field()
    history = scrapy.Field()
    codes = scrapy.Field()
    modality = scrapy.Field()
    session_at = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()


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
