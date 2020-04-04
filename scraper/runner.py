import argparse
from datetime import datetime, timedelta

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def run_crawlers(start_from_date):
    process = CrawlerProcess(get_project_settings())

    process.crawl("cityhall_payments", start_from_date=start_from_date)
    process.crawl("cityhall_contracts", start_from_date=start_from_date)

    process.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all", help="Coleta todos os itens desde a data inicial.", action="store_true"
    )
    args = parser.parse_args()
    if args.all:
        start_from_date = None
    else:
        yesterday = datetime.now() - timedelta(days=1)
        start_from_date = yesterday.date()

    run_crawlers(start_from_date)
