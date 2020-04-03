import re

import pytest
from model_bakery import baker

from datasets.management.commands.searchvector import Command
from datasets.models import Gazette


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

        gazette = baker.make(Gazette, file_content=text)
        gazette.save()

        command = Command()
        command.handle()

        gazette.refresh_from_db()

        captured = capsys.readouterr()
        assert re.search(r"Creating search vector.*Total items: 1", captured.out)
        assert "Done!" in captured.out

        assert gazette.search_vector == answer
