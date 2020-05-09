from django.contrib import admin
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from django.utils.safestring import mark_safe

from .models import (
    CityCouncilAgenda,
    CityCouncilAttendanceList,
    CityCouncilExpense,
    CityCouncilMinute,
    CityHallBid,
    Gazette,
    File,
)


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
    search_fields = ["year_and_edition"]
    list_filter = ["power", "date"]
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
        file_ = obj.files.first()
        return f"<a href={file_.url}>{file_.url}</a>"

    @mark_safe
    def page(self, obj):
        return f"<a href={obj.crawled_from}>{obj.crawled_from}</a>"


@admin.register(CityCouncilAgenda)
class CityCouncilAgendaAdmin(ReadOnlyMixin, admin.ModelAdmin):
    ordering = ["-date"]
    search_fields = ["title", "details"]
    list_filter = ["date", "event_type"]
    list_display = (
        "date",
        "title",
        "event_type",
        "details",
        "crawled_at",
        "crawled_from",
    )


@admin.register(CityCouncilAttendanceList)
class CityCouncilAttendanceListAdmin(ReadOnlyMixin, admin.ModelAdmin):
    ordering = ["-date"]
    list_filter = ["date", "status", "council_member"]
    list_display = (
        "date",
        "description",
        "council_member",
        "status",
        "crawled_at",
        "crawled_from",
    )


@admin.register(CityCouncilExpense)
class CityCouncilExpenseAdmin(ReadOnlyMixin, admin.ModelAdmin):
    ordering = ["-date"]
    search_fields = ["summary", "document", "number", "process_number"]
    list_filter = [
        "date",
        "subgroup",
        "group",
        "type_of_process",
        "phase",
        "company_or_person",
    ]
    list_display = (
        "date",
        "phase",
        "company_or_person",
        "summary",
        "value",
        "subgroup",
        "group",
        "type_of_process",
        "number",
        "process_number",
    )


@admin.register(CityCouncilMinute)
class CityCouncilMinuteAdmin(ReadOnlyMixin, admin.ModelAdmin):
    ordering = ["-date"]
    search_fields = ["title", "file_content"]
    list_filter = ["date", "event_type"]
    list_display = (
        "date",
        "title",
        "event_type",
        "files",
        "crawled_at",
        "crawled_from",
    )

    @mark_safe
    def files(self, obj):
        return "<br>".join(
            [f"<a href={file_.url}>{file_.url}</a>" for file_ in obj.files.all()]
        )

    files.short_description = "Arquivos"


@admin.register(CityHallBid)
class CityHallBidAdmin(ReadOnlyMixin, admin.ModelAdmin):
    ordering = ["-session_at"]
    search_fields = ["description", "codes", "file_content"]
    list_filter = ["session_at", "public_agency", "modality"]
    list_display = (
        "session_at",
        "public_agency",
        "codes",
        "modality",
        "description",
        "events",
        "files",
    )

    @mark_safe
    def files(self, obj):
        return "<br>".join(
            [f"<a href={file_.url}>{file_.url}</a>" for file_ in obj.files.all()]
        )

    files.short_description = "Arquivos"

    @mark_safe
    def events(self, obj):
        to_be_displayed = []
        for event in obj.events.all():
            event_label = f"{event.published_at}: {event.summary} "
            for url in event.file_urls:
                event_label += f"<a href={url}>{url}</a>"
            to_be_displayed.append(event_label)

        return "<br><br>".join(to_be_displayed)

    events.short_description = "Histórico"


@admin.register(File)
class FileAdmin(ReadOnlyMixin, admin.ModelAdmin):
    ordering = ["-created_at"]
    search_fields = ["search_vector", "content"]
    list_filter = ["content_type"]
    list_display = (
        "created_at",
        "updated_at",
        "url",
        "from_",
    )

    @mark_safe
    def from_(self, obj):
        return obj.content_object

    from_.short_description = "Origem"

    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return super().get_search_results(request, queryset, search_term)

        query = SearchQuery(search_term, config="portuguese")
        rank = SearchRank(F("search_vector"), query)
        queryset = (
            File.objects.annotate(rank=rank)
            .filter(search_vector=query)
            .order_by("-rank")
        )

        return queryset, False
