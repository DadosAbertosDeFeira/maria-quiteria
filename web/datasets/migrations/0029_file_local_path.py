# Generated by Django 3.2.7 on 2021-09-23 08:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0028_auto_20210703_0457"),
    ]

    operations = [
        migrations.AddField(
            model_name="file",
            name="local_path",
            field=models.CharField(blank=True, max_length=350, null=True),
        ),
    ]
