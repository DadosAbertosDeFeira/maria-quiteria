from datetime import datetime, timedelta

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


process = CrawlerProcess(get_project_settings())

# TODO receber via CLI se todos ou não

yesterday = datetime.now() - timedelta(days=1)
yesterday = yesterday.date()

process.crawl("cityhall_payments", start_date=yesterday)
process.start()
