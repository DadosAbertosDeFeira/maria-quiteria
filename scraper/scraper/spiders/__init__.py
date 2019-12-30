import scrapy


class BaseSpider(scrapy.Spider):
    start_from_date = None

    @property
    def start_date(self):
        if self.start_from_date:
            picked_date = self.start_from_date
        else:
            picked_date = self.initial_date

        return picked_date

    @property
    def collect_all(self):
        return bool(self.start_from_date) is False
