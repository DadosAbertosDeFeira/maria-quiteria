import scrapy
from dateutil.parser import parse


class BaseSpider(scrapy.Spider):
    start_from_date = None

    @property
    def start_date(self):
        picked_date = None
        if self.start_from_date:
            if isinstance(self.start_from_date, str):
                picked_date = parse(self.start_from_date, dayfirst=True)
                picked_date = picked_date.date()
            else:
                picked_date = self.start_from_date
        elif hasattr(self, "initial_date"):
            picked_date = self.initial_date

        return picked_date
