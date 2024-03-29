# Generated by Django 3.0 on 2020-02-02 02:00

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CityCouncilAgenda",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("crawled_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("crawled_from", models.URLField(blank=True, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                ("date", models.DateField()),
                ("details", models.TextField(blank=True, null=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("ordem_do_dia", "Ordem do Dia"),
                            ("sessao_solene", "Sessão Solene"),
                            ("sessao_especial", "Sessão Especial"),
                            ("audiencia_publica", "Audiência Pública"),
                        ],
                        max_length=20,
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
