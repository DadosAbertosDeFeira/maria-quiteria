from django.contrib import admin
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from django.utils.safestring import mark_safe
from public_admin.admin import PublicModelAdmin
from public_admin.sites import PublicAdminSite, PublicApp

from .models import (
    CityCouncilAgenda,
    CityCouncilAttendanceList,
    CityCouncilMinute,
    CityCouncilRevenue,
    CityHallBid,
    File,
    Gazette,
)


class GazetteAdmin(PublicModelAdmin):
    ordering = ["-date"]
    search_fields = ["year_and_edition", "events__summary", "files__search_vector"]
    list_filter = ["power", "date"]
    list_display = (
        "date",
        "power",
        "year_and_edition",
        "events",
        "url",
        "crawled_at",
        "crawled_from",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("files", "events")

    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return super().get_search_results(request, queryset, search_term)

        # FIXME ordenação das colunas não funciona quando tem um search_term

        query = SearchQuery(search_term, config="portuguese")
        rank = SearchRank(F("files__search_vector"), query)
        queryset = (
            queryset.annotate(rank=rank)
            .filter(files__search_vector=query)
            .order_by("-rank")
        )

        return queryset, False

    @mark_safe
    def events(self, obj):
        return "<br><br>".join(
            [
                f"{event.title} ({event.secretariat}): {event.summary}"
                for event in obj.events.all()
            ]
        )

    events.short_description = "Eventos"

    @mark_safe
    def url(self, obj):
        file_ = obj.files.first()
        if file_:
            return f"<a href={file_.url}>{file_.url}</a>"
        return ""

    url.short_description = "Endereço (URL)"


class CityCouncilAgendaAdmin(PublicModelAdmin):
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
    list_filter = ["date", "status", "council_member"]
    list_display = (
        "date",
        "description",
        "council_member",
        "status",
        "crawled_at",
        "crawled_from",
    )


class CityCouncilContractAdmin(PublicModelAdmin):
    search_fields = ["details", "description", "company_or_person"]
    list_filter = [
        "start_date",
        "end_date",
        "company_or_person",
    ]
    list_display = (
        "start_date",
        "end_date",
        "company_or_person",
        "company_or_person_document",
        "description",
        "details_with_html",
        "value",
    )

    @mark_safe
    def details_with_html(self, obj):
        return obj.details

    details_with_html.short_description = "Detalhes"


class CityCouncilExpenseAdmin(PublicModelAdmin):
    search_fields = ["summary", "document", "number", "process_number"]
    list_filter = [
        "date",
        "modality",
        "phase",
        "company_or_person",
    ]
    list_display = (
        "date",
        "phase",
        "company_or_person",
        "document",
        "summary",
        "value",
        "legal_status",
        "modality",
        "number",
        "process_number",
    )


class CityCouncilMinuteAdmin(PublicModelAdmin):
    search_fields = ["title", "files__search_vector"]
    list_filter = ["date", "event_type"]
    list_display = (
        "date",
        "title",
        "event_type",
        "files",
        "crawled_at",
        "crawled_from",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("files")

    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return super().get_search_results(request, queryset, search_term)

        query = SearchQuery(search_term, config="portuguese")
        rank = SearchRank(F("files__search_vector"), query)
        queryset = (
            queryset.annotate(rank=rank)
            .filter(files__search_vector=query)
            .order_by("-rank")
        )

        return queryset, False

    @mark_safe
    def files(self, obj):
        return "<br>".join(
            f"<a href={file_.url}>{file_.url}</a>" for file_ in obj.files.all()
        )

    files.short_description = "Arquivos"


class CityHallBidAdmin(PublicModelAdmin):
    search_fields = ["description", "codes", "files__search_vector"]
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

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("files", "events", "events__files")
        )

    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return super().get_search_results(request, queryset, search_term)

        query = SearchQuery(search_term, config="portuguese")
        rank = SearchRank(F("files__search_vector"), query)
        queryset = (
            queryset.annotate(rank=rank)
            .filter(files__search_vector=query)
            .order_by("-rank")
        )

        return queryset, False

    @mark_safe
    def files(self, obj):
        return "<br>".join(
            f"<a href={file_.url}>{file_.url}</a>" for file_ in obj.files.all()
        )

    files.short_description = "Arquivos"

    @mark_safe
    def events(self, obj):
        formatted_events = []
        for event in obj.events.all():
            formatted_date = event.published_at.strftime("%d/%m/%Y %H:%m")
            urls = ""
            if event.file_urls:
                urls = "<br>".join(
                    [f"<a href={url}>{url}</a>" for url in event.file_urls]
                )
            formatted_events.append(f"{formatted_date}<br>{event.summary}<br>{urls}")
        return "<br><br>".join(formatted_events)

    events.short_description = "Histórico"


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    search_fields = ["search_vector"]
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
            queryset.annotate(rank=rank).filter(search_vector=query).order_by("-rank")
        )

        return queryset, False


class CityCouncilBidAdmin(PublicModelAdmin):
    search_fields = ["description", "code", "code_type"]
    list_filter = ["session_at", "modality"]
    list_display = (
        "session_at",
        "modality",
        "code",
        "code_type",
        "description_html",
    )

    @mark_safe
    def description_html(self, obj):
        return obj.description

    description_html.short_description = "Descrição"


class CityCouncilRevenueAdmin(PublicModelAdmin):
    list_filter = [
        "published_at",
        "modality",
        "revenue_type",
        "resource",
        "destination",
    ]
    list_display = (
        "published_at",
        "registered_at",
        "revenue_type",
        "modality",
        "description",
        "value",
        "legal_status",
        "destination",
    )


class MariaQuiteriaPublicAdminSite(PublicAdminSite):
    site_title = "Dados Abertos de Feira"
    site_header = "Dados Abertos de Feira"
    index_title = "Painel de buscas"


public_app = PublicApp("datasets", models=())
public_admin = MariaQuiteriaPublicAdminSite(public_apps=public_app)
models_and_admins = [
    (CityCouncilAgenda, CityCouncilAgendaAdmin),
    (CityCouncilAttendanceList, CityCouncilAttendanceListAdmin),
    # aguardando completar a migração com a Câmara
    # (CityCouncilBid, CityCouncilBidAdmin),
    # (CityCouncilContract, CityCouncilContractAdmin),
    # (CityCouncilExpense, CityCouncilExpenseAdmin),
    (CityCouncilMinute, CityCouncilMinuteAdmin),
    (CityCouncilRevenue, CityCouncilRevenueAdmin),
    (Gazette, GazetteAdmin),
    (CityHallBid, CityHallBidAdmin),
]

for model, admin_class in models_and_admins:
    public_admin.register(model, admin_class)
