from django.apps import AppConfig


class DatasetsConfig(AppConfig):
    name = "datasets"
    verbose_name = "Bases de dados"

    def ready(self):
        import datasets.signals  # noqa
