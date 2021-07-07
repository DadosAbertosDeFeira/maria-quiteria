from django_filters import rest_framework as filters
from web.datasets.models import Gazette


class GazetteFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Gazette
        fields = ["power", "start_date", "end_date"]
