from django.contrib.postgres.search import SearchVector
from django.core.management.base import BaseCommand

from datasets.models import Gazette


class Command(BaseCommand):
    def handle(self, *args, **options):
        gazette_count = Gazette.objects.count()
        print(f"Creating search vector for Gazette. Total items: {gazette_count}")
        print("Please wait...")

        search_vector = SearchVector("file_content", config="portuguese")

        Gazette.objects.update(search_vector=search_vector)

        print("Done!")
