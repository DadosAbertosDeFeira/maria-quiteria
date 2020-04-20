from datetime import date, datetime

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import F

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
    def last_collected_item_date(cls):
        try:
            field = cls._meta.get_latest_by
            kwargs = {
                f"{field}__isnull": False,
            }
            found = cls.objects.filter(**kwargs).latest()
            if found:
                value = getattr(found, field)
                if isinstance(value, datetime):
                    return value.date()
                return value
        except cls.DoesNotExist:
            return
        except TypeError:
            raise NotImplementedError(
                "Especifique um `get_latest_by` no Meta deste model"
            )


class CityCouncilAgenda(DatasetMixin):
    date = models.DateField()
    details = models.TextField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=CITY_COUNCIL_EVENT_TYPE)
    title = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Câmara de Vereadores - Agenda"
        verbose_name_plural = "Câmara de Vereadores - Agendas"
        get_latest_by = "date"

    def __repr__(self):
        return f"{self.date} {self.event_type} {self.title}"

    @classmethod
    def last_collected_item_date(cls):
        """Retorna primeiro dia do ano do mais recente item coletado."""
        try:
            latest = cls.objects.latest()
            if latest.date:
                return date(latest.date.year, 1, 1)
        except cls.DoesNotExist:
            return


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
        get_latest_by = "date"

    def __repr__(self):
        return f"{self.date} {self.council_member} {self.status}"

    @classmethod
    def last_collected_item_date(cls):
        """Retorna primeiro dia do ano do mais recente item coletado."""
        try:
            latest = cls.objects.latest()
            if latest.date:
                return date(latest.date.year, 1, 1)
        except cls.DoesNotExist:
            return


class CityCouncilExpense(DatasetMixin):
    PHASE = (
        ("empenho", "Empenho"),
        ("liquidacao", "Liquidação"),
        ("pagamento", "Pagamento"),
    )
    published_at = models.DateField()
    phase = models.CharField(max_length=20, choices=PHASE)
    company_or_person = models.TextField(null=True, blank=True)
    value = models.DecimalField("Valor", max_digits=10, decimal_places=2)
    number = models.CharField(max_length=50, null=True, blank=True)
    document = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField()
    process_number = models.CharField(max_length=50, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    legal_status = models.CharField(max_length=200, null=True, blank=True)
    function = models.CharField(max_length=50, null=True, blank=True)
    subfunction = models.CharField(max_length=50, null=True, blank=True)
    type_of_process = models.CharField(max_length=50, null=True, blank=True)
    resource = models.CharField(max_length=200, null=True, blank=True)
    subgroup = models.CharField(max_length=100, null=True, blank=True)
    group = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Câmara de Vereadores - Despesa"
        verbose_name_plural = "Câmara de Vereadores - Despesas"
        get_latest_by = "date"

    def __repr__(self):
        return f"{self.date} {self.phase} {self.company_or_person} {self.value}"

    def __str__(self):
        return f"{self.date} {self.phase} {self.company_or_person} {self.value}"


class CityCouncilMinute(DatasetMixin):
    date = models.DateField()
    title = models.CharField(max_length=300, null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=CITY_COUNCIL_EVENT_TYPE)
    file_url = models.URLField(null=True, blank=True)
    file_content = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Câmara de Vereadores - Atas"
        verbose_name_plural = "Câmara de Vereadores - Atas"
        get_latest_by = "date"

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
    checksum = models.CharField(max_length=128, null=True, blank=True)

    search_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        verbose_name = "Diário Oficial"
        verbose_name_plural = "Diários Oficiais"
        get_latest_by = "date"
        ordering = [F("date").desc(nulls_last=True)]

        indexes = [GinIndex(fields=["search_vector"])]

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
