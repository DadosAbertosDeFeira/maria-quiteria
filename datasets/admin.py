from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Gazette


class ReadOnlyMixin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Gazette)
class GazetteAdmin(ReadOnlyMixin, admin.ModelAdmin):
    ordering = ["-date"]
    search_fields = ["year_and_edition", "file_content"]
    list_filter = ["power", "year_and_edition"]
    list_display = (
        "date",
        "power",
        "year_and_edition",
        "events",
        "url",
        "crawled_at",
        "page",
    )

    @mark_safe
    def events(self, obj):
        return "<br><br>".join(
            [
                f"{event.title} ({event.secretariat}): {event.summary}"
                for event in obj.gazetteevent_set.all()
            ]
        )

    @mark_safe
    def url(self, obj):
        return f"<a href={obj.file_url}>{obj.file_url}</a>"

    @mark_safe
    def page(self, obj):
        return f"<a href={obj.crawled_from}>{obj.crawled_from}</a>"
