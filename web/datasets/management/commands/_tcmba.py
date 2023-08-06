from django.contrib.admin.options import get_content_type_for_model

from web.datasets.models import File, TCMBADocument
from web.datasets.parsers import from_str_to_date


def save_document(item):
    public_view_url = "https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam"
    document, created = TCMBADocument.objects.get_or_create(
        year=item["year"],
        month=item["month"],
        period=item["period"].lower(),
        category=item["category"],
        unit=item["unit"],
        inserted_at=from_str_to_date(item["inserted_at"]),
        inserted_by=item["inserted_by"],
        original_filename=item["original_filename"],
        crawled_from=public_view_url,
        defaults={
            "crawled_at": item["crawled_at"],
        },
    )
    content_type = get_content_type_for_model(document)
    if created:
        _, file_created = File.objects.get_or_create(
            url=public_view_url,
            content_type=content_type,
            object_id=document.pk,
            local_path=f"{item['filepath']}{item['filename']}",
            original_filename=item["original_filename"],
        )
