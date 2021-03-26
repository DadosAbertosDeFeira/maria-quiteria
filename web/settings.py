import os
from datetime import timedelta
from socket import gethostbyname, gethostname

import dj_database_url
import sentry_sdk
from configurations import Configuration, values
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[DjangoIntegration(), CeleryIntegration()],
)


class Common(Configuration):
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    SECRET_KEY = "really-secret"

    DEBUG = False

    ALLOWED_HOSTS = []
    INSTALLED_APPS = [
        "web.home.apps.HomeConfig",
        "public_admin",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "web.datasets.apps.DatasetsConfig",
        "django_extensions",
        "rest_framework",
        "simple_history",
        "django_filters",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "simple_history.middleware.HistoryRequestMiddleware",
    ]

    ROOT_URLCONF = "web.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "web.home.context_processors.google_analytics_key",
                ]
            },
        }
    ]

    WSGI_APPLICATION = "web.wsgi.application"

    default_db = "postgres://postgres:postgres@db:5432/mariaquiteria"
    DATABASES = {"default": dj_database_url.config(default=default_db)}

    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa
        },
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

    LANGUAGE_CODE = "pt-br"
    USE_L10N = False
    DATE_FORMAT = "d/m/Y"
    DATETIME_FORMAT = "d/m/Y H:i"

    TIME_ZONE = "America/Fortaleza"

    USE_I18N = True

    USE_TZ = True

    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    STATIC_URL = "/static/"
    STATICFILES_DIRS = ()
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

    GOOGLE_ANALYTICS_KEY = None

    AWS_ACCESS_KEY_ID = values.Value(environ_prefix=None)
    AWS_SECRET_ACCESS_KEY = values.Value(environ_prefix=None)
    AWS_S3_BUCKET = values.Value(environ_prefix=None)
    AWS_S3_BUCKET_FOLDER = values.Value(environ_prefix=None)
    AWS_S3_REGION = values.Value(environ_prefix=None)

    CITY_COUNCIL_WEBSERVICE = values.Value(
        default="http://teste.com.br/", environ_prefix=None
    )
    CITY_COUNCIL_WEBSERVICE_ENDPOINT = values.Value(
        default="http://teste.com.br/webservice/",
        environ_prefix=None,
    )
    CITY_COUNCIL_WEBSERVICE_TOKEN = values.Value(default="fake", environ_prefix=None)

    CELERY_BROKER_URL = values.Value(
        environ_prefix=None, default="amqp://guest:guest@rabbitmq:5672/"
    )

    REST_FRAMEWORK = {
        "SEARCH_PARAM": "query",
        "DEFAULT_FILTER_BACKENDS": [
            "django_filters.rest_framework.DjangoFilterBackend"
        ],
        "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ),
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 50,
    }

    ACCESS_TOKEN_LIFETIME_IN_MINUTES = int(
        os.getenv("ACCESS_TOKEN_LIFETIME_IN_MINUTES", 1440)  # 24 horas
    )
    REFRESH_TOKEN_LIFETIME_IN_MINUTES = int(
        os.getenv("REFRESH_TOKEN_LIFETIME_IN_MINUTES", 1440)  # 24 horas
    )
    SIMPLE_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(minutes=ACCESS_TOKEN_LIFETIME_IN_MINUTES),
        "REFRESH_TOKEN_LIFETIME": timedelta(minutes=REFRESH_TOKEN_LIFETIME_IN_MINUTES),
        "BLACKLIST_AFTER_ROTATION": False,
    }

    ENABLE_NEW_RELIC = False


class Dev(Common):
    DEBUG = True
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "0.0.0.0"]

    INSTALLED_APPS = Common.INSTALLED_APPS + ["debug_toolbar"]

    MIDDLEWARE = Common.MIDDLEWARE + ["debug_toolbar.middleware.DebugToolbarMiddleware"]

    INTERNAL_IPS = ["127.0.0.1"]


class Test(Dev):
    CELERY_TASK_ALWAYS_EAGER = True


class Prod(Common):
    SECRET_KEY = values.SecretValue()
    ALLOWED_HOSTS = values.ListValue([], environ_name="ALLOWED_HOSTS")
    ALLOWED_HOSTS.extend((gethostname(), gethostbyname(gethostname())))
    DATABASES = {"default": dj_database_url.config(conn_max_age=600, ssl_require=False)}
    GOOGLE_ANALYTICS_KEY = values.Value()
    CITY_COUNCIL_WEBSERVICE = values.Value()
    ENABLE_NEW_RELIC = True
    NEW_RELIC_LICENSE_KEY = os.getenv("NEW_RELIC_LICENSE_KEY", None)
    NEW_RELIC_APP_NAME = os.getenv("NEW_RELIC_APP_NAME", "vm_mariaquiteria")
    NEW_RELIC_CONFIG_FILE = os.getenv("NEW_RELIC_CONFIG_FILE", "newrelic.ini")
