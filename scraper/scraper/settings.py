import os


# general
BOT_NAME = 'maria-quiteria'
SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'
ROBOTSTXT_OBEY = True
COOKIES_ENABLED = False

# file pipeline
ITEM_PIPELINES = {
   'scrapy.pipelines.files.FilesPipeline': 1,
}
FILES_STORE = f'{os.getcwd()}/data/'

# http cache
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 24 hours
