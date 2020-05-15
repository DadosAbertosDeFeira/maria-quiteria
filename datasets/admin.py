from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from django.utils.safestring import mark_safe
from public_admin.admin import PublicModelAdmin
from public_admin.sites import PublicAdminSite, PublicApp

from .models import (
    CityCouncilAgenda,
    CityCouncilAttendanceList,
    CityCouncilExpense,
    CityCouncilMinute,
    CityHallBid,
    Gazette,
)


class GazetteAdmin(PublicModelAdmin):
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


class CityCouncilAgendaAdmin(PublicModelAdmin):
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


class CityCouncilAttendanceListAdmin(PublicModelAdmin):
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


class CityCouncilExpenseAdmin(PublicModelAdmin):
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


class CityCouncilMinuteAdmin(PublicModelAdmin):
    ordering = ["-date"]
    search_fields = ["title", "file_content"]
    list_filter = ["date", "event_type"]
    list_display = (
        "date",
        "title",
        "event_type",
        "url",
        "crawled_at",
        "crawled_from",
    )

    @mark_safe
    def url(self, obj):
        return f"<a href={obj.file_url}>{obj.file_url}</a>"


class CityHallBidAdmin(PublicModelAdmin):
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
        "url",
    )

    @mark_safe
    def url(self, obj):
        return f"<a href={obj.file_url}>{obj.file_url}</a>"

    url.short_description = "Arquivo"

    @mark_safe
    def events(self, obj):
        return "<br><br>".join(
            [
                f"{event.published_at}: {event.summary} "
                f"{event.file_url if event.file_url else ''}"
                for event in obj.events.all()
            ]
        )

    events.short_description = "Histórico"


class MariaQuiteriaPublicAdminSite(PublicAdminSite):
    site_title = "Dados Abertos de Feira"
    site_header = "Dados Abertos de Feira"
    index_title = "Painel de buscas"


public_app = PublicApp("datasets", models=())
public_admin = MariaQuiteriaPublicAdminSite(public_apps=public_app)
models_and_admins = [
    (CityCouncilAgenda, CityCouncilAgendaAdmin),
    (CityCouncilAttendanceList, CityCouncilAttendanceListAdmin),
    (CityCouncilExpense, CityCouncilExpenseAdmin),
    (CityCouncilMinute, CityCouncilMinuteAdmin),
    (Gazette, GazetteAdmin),
    (CityHallBid, CityHallBidAdmin),
]

for model, admin in models_and_admins:
    public_admin.register(model, admin)
