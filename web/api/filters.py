from django_filters import rest_framework as filters
from web.datasets.models import CityHallBid, Gazette


class GazetteFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Gazette
        fields = [
            "power",
            "start_date",
            "end_date",
            "events__title",
            "events__secretariat",
            "events__summary",
            "year_and_edition",
        ]


class CityHallBidFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name="session_at", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="session_at", lookup_expr="lte")

    class Meta:
        model = CityHallBid
        fields = ["public_agency", "description", "modality", "start_date", "end_date"]
