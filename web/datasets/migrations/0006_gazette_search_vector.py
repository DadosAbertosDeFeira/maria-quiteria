# Generated by Django 3.0.5 on 2020-04-03 22:53

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0005_auto_20200327_1348"),
    ]

    operations = [
        migrations.AddField(
            model_name="gazette",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                editable=False, null=True
            ),
        ),
        migrations.AddIndex(
            model_name="gazette",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="datasets_ga_search__1d3d09_gin"
            ),
        ),
        migrations.RunSQL(
            sql="""
            CREATE TRIGGER search_vector_update BEFORE INSERT OR UPDATE
            ON datasets_gazette FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger(search_vector, 'pg_catalog.portuguese', file_content);
            """,
            reverse_sql="DROP TRIGGER IF EXISTS search_vector_update ON datasets_gazette;",
        ),
    ]
