from unittest.mock import patch

import pytest
from django.test import TestCase
from django.utils import lorem_ipsum
from model_bakery import baker

from datasets.management.commands.searchvector import Command
from datasets.models import Gazette


class TestCommandHandler(TestCase):
    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    @patch.object(Gazette.objects, "update")
    def test_handler(self, update):
        command = Command()
        command.handle()

        captured = self.capsys.readouterr()
        self.assertRegex(captured.out, r"Creating search vector.*Total items: 0")
        self.assertRegex(captured.out, r"Done")

        self.assertEqual(1, update.call_count)

    @pytest.mark.django_db
    def test_create_vector(self):
        gazettes = baker.make(Gazette, _quantity=3, file_content=lorem_ipsum.paragraph)

        ids_to_check = []
        for gazette in gazettes:
            gazette.save()
            self.assertTrue(gazette.id)
            self.assertFalse(gazette.search_vector)
            ids_to_check.append(gazette.id)

        command = Command()
        command.handle()

        captured = self.capsys.readouterr()
        self.assertRegex(captured.out, r"Creating.*Gazette.*Total items:.*3")
        self.assertRegex(captured.out, r"Done")

        items = Gazette.objects.filter(pk__in=ids_to_check)
        for item in items:
            self.assertTrue(item.search_vector)
