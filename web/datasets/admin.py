from django.contrib import admin
from django.contrib.postgres.search import SearchQuery
from django.utils.safestring import mark_safe
from public_admin.admin import PublicModelAdmin
from public_admin.sites import PublicAdminSite, PublicApp

from .models import (
    CityCouncilAgenda,
    CityCouncilAttendanceList,
    CityCouncilBid,
    CityCouncilContract,
    CityCouncilExpense,
    CityCouncilMinute,
    CityCouncilRevenue,
    CityHallBid,
    File,
    Gazette,
    SyncInformation,
    TCMBADocument,
)


class FileURLsMixin:
    readonly_fields = ["file_urls", "alternative_urls"]

    @mark_safe
    def file_urls(self, obj):
        return "<br>".join(
            f'<a href="{file_.url}">{file_.url}</a>'
            for file_ in obj.files.all()
            if file_.url
        )

    file_urls.short_description = "Endereços (URLs)"

    @mark_safe
    def alternative_urls(self, obj):
        return "<br>".join(
            f'<a href="{file_.s3_url}">{file_.s3_url}</a>'
            for file_ in obj.files.all()
            if file_.s3_url
        )

    alternative_urls.short_description = "Endereços alternativos (URLs)"


class GazetteAdmin(FileURLsMixin, PublicModelAdmin):
    search_fields = ["year_and_edition", "events__summary", "files__search_vector"]
    list_filter = ["power", "date"]
    list_display = (
        "date",
        "power",
        "year_and_edition",
        "events",
        "file_urls",
        "crawled_at",
        "crawled_from",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("files", "events")
            .defer("files__content")
        )

    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return super().get_search_results(request, queryset, search_term)

        query = SearchQuery(search_term, config="portuguese")
        queryset = queryset.filter(files__search_vector=query)

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


class CityCouncilContractAdmin(FileURLsMixin, PublicModelAdmin):
    search_fields = ["details", "description", "company_or_person"]
    list_filter = [
        "start_date",
        "end_date",
        "company_or_person",
    ]
    list_display = (
        "crawled_at",
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
        "crawled_at",
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


class CityCouncilMinuteAdmin(FileURLsMixin, PublicModelAdmin):
    search_fields = ["title", "files__search_vector"]
    list_filter = ["date", "event_type"]
    list_display = (
        "date",
        "title",
        "event_type",
        "file_urls",
        "crawled_at",
        "crawled_from",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("files")
            .defer("files__content")
        )

    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return super().get_search_results(request, queryset, search_term)

        query = SearchQuery(search_term, config="portuguese")
        queryset = queryset.filter(files__search_vector=query)

        return queryset, False


class CityHallBidAdmin(FileURLsMixin, PublicModelAdmin):
    search_fields = ["description", "codes", "files__search_vector"]
    list_filter = ["session_at", "public_agency", "modality"]
    list_display = (
        "session_at",
        "public_agency",
        "codes",
        "modality",
        "description",
        "events",
        "file_urls",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("files", "events", "events__files")
            .defer("files__content", "events__files__content")
        )

    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return super().get_search_results(request, queryset, search_term)

        query = SearchQuery(search_term, config="portuguese")
        queryset = queryset.filter(files__search_vector=query)

        return queryset, False

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


@admin.register(SyncInformation)
class SyncInformationAdmin(admin.ModelAdmin):
    list_display = (
        "source",
        "date",
        "created_at",
        "succeed",
    )


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
        queryset = queryset.filter(search_vector=query)

        return queryset, False


class CityCouncilBidAdmin(FileURLsMixin, PublicModelAdmin):
    search_fields = ["description", "code", "code_type"]
    list_filter = ["session_at", "modality"]
    list_display = (
        "crawled_at",
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
        "crawled_at",
        "published_at",
        "registered_at",
        "revenue_type",
        "modality",
        "description",
        "value",
        "legal_status",
        "destination",
    )


class TCMBADocumentAdmin(FileURLsMixin, PublicModelAdmin):
    search_fields = ["original_filename", "unit", "category"]
    list_filter = ["month", "year", "period", "unit", "category"]
    list_display = (
        "original_filename",
        "month",
        "year",
        "unit",
        "category",
    )


class MariaQuiteriaPublicAdminSite(PublicAdminSite):
    site_title = "Dados Abertos de Feira"
    site_header = "Dados Abertos de Feira"
    index_title = "Painel de buscas"


models_and_admins = [
    (CityCouncilAgenda, CityCouncilAgendaAdmin),
    (CityCouncilAttendanceList, CityCouncilAttendanceListAdmin),
    (CityCouncilBid, CityCouncilBidAdmin),
    (CityCouncilContract, CityCouncilContractAdmin),
    (CityCouncilExpense, CityCouncilExpenseAdmin),
    (CityCouncilRevenue, CityCouncilRevenueAdmin),
    (CityCouncilMinute, CityCouncilMinuteAdmin),
    (Gazette, GazetteAdmin),
    (CityHallBid, CityHallBidAdmin),
    (TCMBADocument, TCMBADocumentAdmin),
]
public_app = PublicApp(
    "datasets", models=(model[0].__name__ for model in models_and_admins)
)
public_admin = MariaQuiteriaPublicAdminSite(public_apps=public_app)

for model, admin_class in models_and_admins:
    public_admin.register(model, admin_class)
