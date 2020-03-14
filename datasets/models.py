from django.contrib.postgres.fields import ArrayField
from django.db import models


class DatasetMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    crawled_at = models.DateTimeField()
    crawled_from = models.URLField()
    notes = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    @classmethod
    def last_collected_item_date(self):
        try:
            return self.objects.latest("crawled_at").crawled_at.date()
        except self.DoesNotExist:
            return


class CityCouncilAgenda(DatasetMixin):
    EVENT_TYPE = (
        ("ordem_do_dia", "Ordem do Dia"),
        ("sessao_solene", "Sessão Solene"),
        ("sessao_especial", "Sessão Especial"),
        ("audiencia_publica", "Audiência Pública"),
    )
    date = models.DateField()
    details = models.TextField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE)
    title = models.CharField(max_length=100, null=True, blank=True)

    def __repr__(self):
        return f"{self.date} {self.event_type} {self.title}"


class Gazette(DatasetMixin):
    POWER_TYPE = (
        ("executivo", "Poder Executivo"),
        ("legislativo", "Poder Legislativo"),
    )
    date = models.DateField()
    power = models.CharField(max_length=25, choices=POWER_TYPE)
    year_and_edition = models.CharField(max_length=100)
    file_urls = ArrayField(models.URLField(null=True, blank=True), blank=True)
    file_content = models.TextField(null=True, blank=True)

    def __repr__(self):
        return f"{self.date} {self.power} {self.year_and_edition}"


class GazetteEvent(DatasetMixin):
    gazette = models.ForeignKey(Gazette, on_delete=models.CASCADE)
    title = models.CharField(max_length=300, null=True, blank=True)
    secretariat = models.CharField(max_length=100, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)

    def __repr__(self):
        gazette_info = f"{self.gazette.power} {self.gazette.year_and_edition}"
        return f"[{gazette_info}] {self.title} {self.secretariat}"
