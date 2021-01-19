import re

import pytest
from web.datasets.management.commands.searchvector import Command
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
        gazette = baker.make("datasets.File", content=text)
        assert not gazette.search_vector

        command = Command()
        command.handle()

        gazette.refresh_from_db()

        captured = capsys.readouterr()
        assert re.search(r"Criando um vetor .* Total de itens: 1", captured.out)
        assert "Pronto!" in captured.out

        assert gazette.search_vector == answer
