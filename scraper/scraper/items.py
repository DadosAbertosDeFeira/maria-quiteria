import scrapy


class LegacyGazetteItem(scrapy.Item):
    title = scrapy.Field()
    published_on = scrapy.Field()
    date = scrapy.Field()
    details = scrapy.Field()
    file_urls = scrapy.Field()
    crawled_at = scrapy.Field()
    file_content = scrapy.Field()


class GazetteEventItem(scrapy.Item):
    date = scrapy.Field()
    power = scrapy.Field()
    year_and_edition = scrapy.Field()
    crawled_at = scrapy.Field()
    event_title = scrapy.Field()
    event_secretariat = scrapy.Field()
    event_summary = scrapy.Field()
    file_urls = scrapy.Field()
    file_content = scrapy.Field()


class CityCouncilAgendaItem(scrapy.Item):
    crawled_at = scrapy.Field()
    date = scrapy.Field()
    details = scrapy.Field()
    title = scrapy.Field()
    event_type = scrapy.Field()


class CityHallContractItem(scrapy.Item):
    contract_id = scrapy.Field()
    starts_at = scrapy.Field()
    summary = scrapy.Field()
    contractor_document = scrapy.Field()  # CNPJ or CPF
    contractor_name = scrapy.Field()
    value = scrapy.Field()
    ends_at = scrapy.Field()
    file_urls = scrapy.Field()
    file_content = scrapy.Field()
