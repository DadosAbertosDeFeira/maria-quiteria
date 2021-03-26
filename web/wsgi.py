import os

from configurations.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")

application = get_wsgi_application()

if settings.ENABLE_NEW_RELIC:
    import newrelic.agent

    newrelic.agent.initialize(settings.NEW_RELIC_CONFIG_FILE)
    application = newrelic.agent.WSGIApplicationWrapper(application)
