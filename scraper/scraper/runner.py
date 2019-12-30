import argparse
from datetime import datetime, timedelta

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def run_crawlers(start_date):
    process = CrawlerProcess(get_project_settings())

    # FIXME enable this when all spiders are ready
    # for spider in process.spider_loader.list():
    #     process.crawl(spider, start_date=start_date)
    # TODO add flag to daily collect

    process.crawl("cityhall_payments", start_date=start_date)
    process.crawl("cityhall_contracts", start_date=start_date)
    process.crawl("cityhall_bids", start_date=start_date)
    process.crawl("citycouncil_agenda", start_date=start_date)
    process.crawl("gazettes", start_date=start_date)
    process.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all", help="Coleta todos os itens desde a data inicial.", action="store_true"
    )
    args = parser.parse_args()
    if args.all:
        start_date = None
    else:
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.date()

    run_crawlers(start_date)
