import os
from .items import GazetteEventItem, LegacyGazetteItem


# general
BOT_NAME = "maria-quiteria"
SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"
ROBOTSTXT_OBEY = True
COOKIES_ENABLED = False
EXTENSIONS = {
    "spidermon.contrib.scrapy.extensions.Spidermon": 500,
}

# pipelines
ITEM_PIPELINES = {
    "scraper.pipelines.ExtractPDFContentPipeline": 100,
    "spidermon.contrib.scrapy.pipelines.ItemValidationPipeline": 200,
}
FILES_STORE = f"{os.getcwd()}/data/"
KEEP_FILES = os.getenv("KEEP_FILES", False)

# http cache
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 24 hours

# testing
SPIDERMON_ENABLED = True
SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS = True
SPIDERMON_VALIDATION_MODELS = {
    LegacyGazetteItem: "scraper.validators.LegacyGazetteItem",
    GazetteEventItem: "scraper.validators.GazetteEventItem",
}
