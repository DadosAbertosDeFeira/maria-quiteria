import os

from .items import (
    CityCouncilAgendaItem,
    CityCouncilAttendanceListItem,
    CityCouncilMinuteItem,
    CityHallBidItem,
    CityHallContractItem,
    CityHallPaymentsItem,
    GazetteItem,
    LegacyGazetteItem,
)

# general
BOT_NAME = "maria-quiteria"
SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"
ROBOTSTXT_OBEY = True
COOKIES_ENABLED = False
EXTENSIONS = {
    "scraper.extensions.SentryLogging": -1,
    "spidermon.contrib.scrapy.extensions.Spidermon": 500,
}
SENTRY_DSN = os.getenv("SENTRY_DSN", "")

# pipelines
ITEM_PIPELINES = {
    "scraper.pipelines.ExtractFileContentPipeline": 100,
    "spidermon.contrib.scrapy.pipelines.ItemValidationPipeline": 200,
}
FILES_STORE = f"{os.getcwd()}/data/"
KEEP_FILES = os.getenv("KEEP_FILES", False)
ASYNC_FILE_PROCESSING = os.getenv("ASYNC_FILE_PROCESSING", False)

# http cache
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 24 horas

# testing
SPIDERMON_ENABLED = True
SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS = True
SPIDERMON_VALIDATION_MODELS = {
    LegacyGazetteItem: "scraper.validators.LegacyGazetteItem",
    GazetteItem: "scraper.validators.GazetteItem",
    CityCouncilAgendaItem: "scraper.validators.CityCouncilAgendaItem",
    CityCouncilMinuteItem: "scraper.validators.CityCouncilMinuteItem",
    CityHallContractItem: "scraper.validators.CityHallContractItem",
    CityHallBidItem: "scraper.validators.CityHallBidItem",
    CityHallPaymentsItem: "scraper.validators.CityHallPaymentsItem",
    CityCouncilAttendanceListItem: "scraper.validators.CityCouncilAttendanceListItem",
}

# monitoring
SPIDERMON_SPIDER_CLOSE_MONITORS = ("scraper.monitors.SpiderCloseMonitorSuite",)

# bot
SPIDERMON_TELEGRAM_SENDER_TOKEN = os.getenv("SPIDERMON_TELEGRAM_SENDER_TOKEN", "fake")
SPIDERMON_TELEGRAM_RECIPIENTS = [os.getenv("SPIDERMON_TELEGRAM_CHANNEL", None)]
SPIDERMON_TELEGRAM_FAKE = os.getenv("SPIDERMON_TELEGRAM_FAKE", False)

# sentry
SPIDERMON_SENTRY_DSN = SENTRY_DSN
SPIDERMON_SENTRY_PROJECT_NAME = "MariaQuiteria - Scraper"
SPIDERMON_SENTRY_ENVIRONMENT_TYPE = os.getenv(
    "SPIDERMON_SENTRY_ENVIRONMENT_TYPE", "Prod"
)
SPIDERMON_SENTRY_FAKE = os.getenv("SPIDERMON_SENTRY_FAKE", False)
