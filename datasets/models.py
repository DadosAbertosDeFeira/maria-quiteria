from django.db import models


class CityCouncilAgenda(models.Model):
    EVENT_TYPE = (
        ("ordem_do_dia", "Ordem do Dia"),
        ("sessao_solene", "Sessão Solene"),
        ("sessao_especial", "Sessão Especial"),
        ("audiencia_publica", "Audiência Pública"),
    )
    crawled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    crawled_from = models.URLField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    date = models.DateField()
    details = models.TextField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE)
    title = models.CharField(max_length=100, null=True, blank=True)
