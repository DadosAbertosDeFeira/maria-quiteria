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
