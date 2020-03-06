from datetime import datetime

import scrapy


class BaseSpider(scrapy.Spider):
    start_from_date = None

    @property
    def start_date(self):
        picked_date = None
        if self.start_from_date:
            if isinstance(self.start_from_date, str):
                picked_date = datetime.strptime(self.start_from_date, "%d/%m/%Y")
                picked_date = picked_date.date()
            else:
                picked_date = self.start_from_date
        elif hasattr(self, "initial_date"):
            picked_date = self.initial_date

        return picked_date

    @property
    def collect_all(self):
        return bool(self.start_from_date) is False
