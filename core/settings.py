import logging
import os

import dj_database_url
import sentry_sdk
from configurations import Configuration, values
from sentry_dramatiq import DramatiqIntegration
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[DjangoIntegration(), DramatiqIntegration()],
)

logging.getLogger("pika").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)


class Common(Configuration):
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    SECRET_KEY = "really-secret"

    DEBUG = False

    ALLOWED_HOSTS = []
    INSTALLED_APPS = [
        "home",
        "public_admin",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "datasets.apps.DatasetsConfig",
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
    ]

    ROOT_URLCONF = "core.urls"

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
                    "home.context_processors.google_analytics_key",
                ],
            },
        }
    ]

    WSGI_APPLICATION = "core.wsgi.application"

    default_db = "postgres://USER:PASSWORD@HOST:PORT/NAME"
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
    ASYNC_FILE_PROCESSING = values.Value(default=True, environ_prefix=None)

    AWS_ACCESS_KEY_ID = values.Value(environ_prefix=None)
    AWS_SECRET_ACCESS_KEY = values.Value(environ_prefix=None)
    AWS_S3_BUCKET = values.Value(environ_prefix=None)
    AWS_S3_BUCKET_FOLDER = values.Value(environ_prefix=None)
    AWS_S3_REGION = values.Value(environ_prefix=None)


class Dev(Common):
    DEBUG = True
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "0.0.0.0"]
    CLOUDAMQP_URL = "amqp://localhost:5672"

    INSTALLED_APPS = Common.INSTALLED_APPS + ["debug_toolbar"]

    MIDDLEWARE = Common.MIDDLEWARE + ["debug_toolbar.middleware.DebugToolbarMiddleware"]

    INTERNAL_IPS = ["127.0.0.1"]


class Prod(Common):
    SECRET_KEY = values.SecretValue()
    ALLOWED_HOSTS = values.ListValue()
    CLOUDAMQP_URL = values.Value(environ_prefix=None)

    DATABASES = {"default": dj_database_url.config(conn_max_age=600, ssl_require=True)}
    GOOGLE_ANALYTICS_KEY = values.Value()
