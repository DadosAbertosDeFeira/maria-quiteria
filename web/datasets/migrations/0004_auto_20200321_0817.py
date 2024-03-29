# Generated by Django 3.0 on 2020-03-21 11:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0003_citycouncilattendancelist"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="citycouncilagenda",
            options={
                "verbose_name": "Câmara de Vereadores - Agenda",
                "verbose_name_plural": "Câmara de Vereadores - Agendas",
            },
        ),
        migrations.AlterModelOptions(
            name="citycouncilattendancelist",
            options={
                "verbose_name": "Câmara de Vereadores - Lista de Presença",
                "verbose_name_plural": "Câmara de Vereadores - Listas de Presença",
            },
        ),
        migrations.AlterModelOptions(
            name="gazette",
            options={
                "verbose_name": "Diário Oficial",
                "verbose_name_plural": "Diários Oficiais",
            },
        ),
        migrations.AlterModelOptions(
            name="gazetteevent",
            options={
                "verbose_name": "Diário Oficial - Evento",
                "verbose_name_plural": "Diário Oficial - Eventos",
            },
        ),
    ]
