from django.db import models

CITY_COUNCIL_EVENT_TYPE = (
    ("sessao_ordinaria", "Sessão Ordinária"),
    ("ordem_do_dia", "Ordem do Dia"),
    ("sessao_solene", "Sessão Solene"),
    ("sessao_especial", "Sessão Especial"),
    ("audiencia_publica", "Audiência Pública"),
)


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
    date = models.DateField()
    details = models.TextField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=CITY_COUNCIL_EVENT_TYPE)
    title = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Câmara de Vereadores - Agenda"
        verbose_name_plural = "Câmara de Vereadores - Agendas"

    def __repr__(self):
        return f"{self.date} {self.event_type} {self.title}"


class CityCouncilMinute(DatasetMixin):
    date = models.DateField()
    title = models.CharField(max_length=300, null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=CITY_COUNCIL_EVENT_TYPE)
    file_url = models.URLField(null=True, blank=True)
    file_content = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Câmara de Vereadores - Atas"
        verbose_name_plural = "Câmara de Vereadores - Atas"

    def __repr__(self):
        return f"{self.date} {self.title} {self.file_url}"


class Gazette(DatasetMixin):
    POWER_TYPE = (
        ("executivo", "Poder Executivo"),
        ("legislativo", "Poder Legislativo"),
    )
    date = models.DateField(null=True)
    power = models.CharField(max_length=25, choices=POWER_TYPE)
    year_and_edition = models.CharField(max_length=100)
    is_legacy = models.BooleanField(default=False)
    file_url = models.URLField(null=True, blank=True)
    file_content = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Diário Oficial"
        verbose_name_plural = "Diários Oficiais"

    def __repr__(self):
        return f"{self.date} {self.power} {self.year_and_edition}"

    def __str__(self):
        return f"{self.date} {self.power} {self.year_and_edition}"


class GazetteEvent(DatasetMixin):
    gazette = models.ForeignKey(Gazette, on_delete=models.CASCADE)
    title = models.CharField(max_length=300, null=True, blank=True)
    secretariat = models.CharField(max_length=100, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    published_on = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Diário Oficial - Evento"
        verbose_name_plural = "Diário Oficial - Eventos"

    def __repr__(self):
        gazette_info = f"{self.gazette.power} {self.gazette.year_and_edition}"
        return f"[{gazette_info}] {self.title} {self.secretariat}"


class CityCouncilAttendanceList(DatasetMixin):
    STATUS = (
        ("presente", "Presente"),
        ("falta_justificada", "Falta Justificada"),
        ("licenca_justificada", "Licença Justificada"),
        ("ausente", "Ausente"),
    )
    date = models.DateField()
    description = models.CharField(max_length=200, null=True, blank=True)
    council_member = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS)

    class Meta:
        verbose_name = "Câmara de Vereadores - Lista de Presença"
        verbose_name_plural = "Câmara de Vereadores - Listas de Presença"

    def __repr__(self):
        return f"{self.date} {self.council_member} {self.status}"
