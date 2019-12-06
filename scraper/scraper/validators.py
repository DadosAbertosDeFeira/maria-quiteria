from schematics.models import Model
from schematics.types import DateType, StringType, URLType


class LegacyGazetteItem(Model):
    title = StringType(required=True)
    published_on = StringType(required=False)
    # important info but not available in years like 2010
    date = DateType(required=False, formats=('%d/%m/%Y', '%d/%m/%y'))
    details = StringType(required=True)
    url = URLType(required=True)
    crawled_at = URLType(required=True)
