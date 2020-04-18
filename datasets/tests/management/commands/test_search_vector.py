import re

import pytest
from datasets.management.commands.searchvector import Command
from django.db import connection
from model_bakery import baker


@pytest.mark.django_db
class TestCommandHandler:
    @pytest.mark.parametrize(
        "text,answer",
        [
            ("O Prefeito Municipal de Feira...", "'feir':5 'municipal':3 'prefeit':2"),
            (
                "Mussum Ipsum, cacilds vidis litro abertis.",
                "'abert':6 'cacilds':3 'ipsum':2 'litr':5 'mussum':1 'vid':4",
            ),
        ],
    )
    def test_handler(self, text, answer, capsys):

        with connection.cursor() as cursor:
            cursor.execute(
                'ALTER TABLE "datasets_gazette" DISABLE TRIGGER search_vector_update;'
            )

            gazette = baker.make_recipe(
                "datasets.Gazette", file_content=text, _refresh_after_create=True
            )
            assert not gazette.search_vector

            command = Command()
            command.handle()

            gazette.refresh_from_db()

            captured = capsys.readouterr()
            assert re.search(r"Creating search vector.*Total items: 1", captured.out)
            assert "Done!" in captured.out

            assert gazette.search_vector == answer

            cursor.execute(
                'ALTER TABLE "datasets_gazette" ENABLE TRIGGER search_vector_update;'
            )
