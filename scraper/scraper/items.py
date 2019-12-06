import scrapy


class LegacyGazetteItem(scrapy.Item):
    title = scrapy.Field()
    published_on = scrapy.Field()
    date = scrapy.Field()
    details = scrapy.Field()
    url = scrapy.Field()
    crawled_at = scrapy.Field()
