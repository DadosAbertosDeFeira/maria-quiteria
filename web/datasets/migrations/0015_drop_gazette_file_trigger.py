from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0014_citycouncilbid"),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TRIGGER IF EXISTS search_vector_update ON datasets_gazette;",
            reverse_sql="""
                CREATE TRIGGER search_vector_update BEFORE INSERT OR UPDATE
                ON datasets_gazette FOR EACH ROW EXECUTE PROCEDURE
                tsvector_update_trigger(search_vector, 'pg_catalog.portuguese', file_content);
            """,
        ),
    ]
