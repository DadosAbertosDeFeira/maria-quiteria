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


class CityCouncilAgenda(models.Model):
    EVENT_TYPE = (
        ("ordem_do_dia", "Ordem do Dia"),
        ("sessao_solene", "Sessão Solene"),
        ("sessao_especial", "Sessão Especial"),
        ("audiencia_publica", "Audiência Pública"),
        ("outro", "Outro"),  # FIXME logar warning quando aparecer outro
    )
    crawled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    crawled_from = models.URLField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    date = models.DateField()
    details = models.TextField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE)
    title = models.CharField(max_length=100, null=True, blank=True)

    def __repr__(self):
        return f"{self.date} {self.event_type} {self.title} ({self.updated_at})"


class Employee(models.Model):
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

    @classmethod
    def last_collected_item_date(self):
        try:
            return self.objects.latest("crawled_at").crawled_at.date()
        except self.DoesNotExist:
            return
