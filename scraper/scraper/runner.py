import argparse
from datetime import datetime, timedelta

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def run_crawlers(start_date):
    process = CrawlerProcess(get_project_settings())

    process.crawl("cityhall_payments", start_date=start_date)
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
