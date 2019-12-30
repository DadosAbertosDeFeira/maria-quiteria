import scrapy


class BaseSpider(scrapy.Spider):
    @property
    def start_date(self):
        if hasattr(self, "start_from_date") and self.start_from_date:
            picked_date = self.start_from_date
        else:
            picked_date = self.initial_date

        return picked_date
