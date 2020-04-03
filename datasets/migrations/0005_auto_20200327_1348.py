# Generated by Django 3.0 on 2020-03-27 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datasets", "0004_auto_20200321_0817"),
    ]

    operations = [
        migrations.CreateModel(
            name="CityCouncilMinute",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("crawled_at", models.DateTimeField()),
                ("crawled_from", models.URLField()),
                ("notes", models.TextField(blank=True, null=True)),
                ("date", models.DateField()),
                ("title", models.CharField(blank=True, max_length=300, null=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("sessao_ordinaria", "Sessão Ordinária"),
                            ("ordem_do_dia", "Ordem do Dia"),
                            ("sessao_solene", "Sessão Solene"),
                            ("sessao_especial", "Sessão Especial"),
                            ("audiencia_publica", "Audiência Pública"),
                        ],
                        max_length=20,
                    ),
                ),
                ("file_url", models.URLField(blank=True, null=True)),
                ("file_content", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Câmara de Vereadores - Atas",
                "verbose_name_plural": "Câmara de Vereadores - Atas",
            },
        ),
        migrations.AlterField(
            model_name="citycouncilagenda",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("sessao_ordinaria", "Sessão Ordinária"),
                    ("ordem_do_dia", "Ordem do Dia"),
                    ("sessao_solene", "Sessão Solene"),
                    ("sessao_especial", "Sessão Especial"),
                    ("audiencia_publica", "Audiência Pública"),
                ],
                max_length=20,
            ),
        ),
    ]
