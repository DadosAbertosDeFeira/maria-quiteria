from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("datasets", "0010_file"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TRIGGER search_vector_file_update BEFORE INSERT OR UPDATE
            ON datasets_file FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger(search_vector, 'pg_catalog.portuguese', content);
            """,
            reverse_sql="DROP TRIGGER IF EXISTS search_vector_file_update ON datasets_file;",
        ),
    ]
