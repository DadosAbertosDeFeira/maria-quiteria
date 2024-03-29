from django.apps import AppConfig


class DatasetsConfig(AppConfig):
    name = "web.datasets"
    verbose_name = "Bases de dados"

    def ready(self):
        import web.datasets.signals  # noqa
