from unittest.mock import patch

import pytest
from django.test import TestCase

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
