import sentry_sdk
from scrapy.exceptions import NotConfigured


class SentryLogging(object):
    """
    Envia exceções e erros para o Sentry.

    Copiado de: https://stackoverflow.com/a/54964660/1344295
    """

    @classmethod
    def from_crawler(cls, crawler):
        sentry_dsn = crawler.settings.get("SENTRY_DSN", None)
        if sentry_dsn is None:
            raise NotConfigured
        ext = cls()
        sentry_sdk.init(sentry_dsn)
        return ext
