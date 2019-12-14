from schematics.models import Model
from schematics.types import DateType, ListType, StringType, URLType


class LegacyGazetteItem(Model):
    title = StringType(required=True)
    published_on = StringType(required=False)
    # important info but not available in years like 2010
    date = DateType(required=False, formats=("%d/%m/%Y", "%d/%m/%y"))
    details = StringType(required=True)
    url = URLType(required=True)
    crawled_at = URLType(required=True)
    file_content = StringType()


class GazetteEventItem(Model):
    date = DateType(formats=("%d/%m/%Y", "%d/%m/%y"))
    power = StringType(required=True)
    year_and_edition = StringType(required=True)
    crawled_at = URLType(required=True)
    event_title = StringType(required=True)
    event_secretariat = StringType(required=True)
    event_summary = StringType(required=True)
    file_urls = ListType(StringType)
    file_content = StringType()


class CityCouncilAgendaItem(Model):
    crawled_at = URLType(required=True)
    date = DateType(formats=("%d/%m/%Y", "%d/%m/%y"))
    details = StringType()
    title = StringType(required=True)
    event_type = StringType(required=True)
