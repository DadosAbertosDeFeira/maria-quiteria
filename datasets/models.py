from django.db import models


class Month(models.IntegerChoices):
    JANEIRO = 1
    FEVEREIRO = 2
    MARCO = 3
    ABRIL = 4
    MAIO = 5
    JUNHO = 6
    JULHO = 7
    AGOSTO = 8
    SETEMBRO = 9
    OUTUBRO = 10
    NOVEMBRO = 11
    DEZEMBRO = 12


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
        ("outro", "Outro"),  # FIXME logar warning quando aparecer outro
    )
    date = models.DateField()
    details = models.TextField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE)
    title = models.CharField(max_length=100, null=True, blank=True)

    def __repr__(self):
        return f"{self.date} {self.event_type} {self.title}"


class Employee(DatasetMixin):
    crawled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    crawled_from = models.URLField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    agency = models.CharField(max_length=200)
    month = models.IntegerField(choices=Month.choices)
    year = models.IntegerField()
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100)
    condition = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    base_salary = models.FloatField()
    benefits_salary = models.FloatField()
    bonus_salary = models.FloatField()
    workload = models.IntegerField()
    status = models.CharField(max_length=200)
    admission = models.DateField()


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

    def __repr__(self):
        gazette_info = f"{self.gazette.power} {self.gazette.year_and_edition}"
        return f"[{gazette_info}] {self.title} {self.secretariat}"
