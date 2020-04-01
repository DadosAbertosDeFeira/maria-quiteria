from django.contrib import admin
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from django.utils.safestring import mark_safe

from .models import CityCouncilAgenda, CityCouncilAttendanceList, Gazette


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
    search_fields = ["year_and_edition", "search_vector"]
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
        return f"<a href={obj.file_url}>{obj.file_url}</a>"

    @mark_safe
    def page(self, obj):
        return f"<a href={obj.crawled_from}>{obj.crawled_from}</a>"

    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return super().get_search_results(request, queryset, search_term)

        query = SearchQuery(search_term, config="portuguese")
        rank = SearchRank(F("search_vector"), query)
        queryset = (
            Gazette.objects.annotate(rank=rank)
            .filter(search_vector=query)
            .order_by("-rank")
        )

        return queryset, False


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
