from django_dramatiq.management.commands.rundramatiq import (
    Command as RunDramatiqCommand,
)


class Command(RunDramatiqCommand):
    """Comando rundramatiq customizado para rodar com o django-configurations."""

    def discover_tasks_modules(self):
        tasks_modules = super().discover_tasks_modules()
        tasks_modules[0] = "web.datasets.dramatiq_setup"
        return tasks_modules
