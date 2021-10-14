from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet
from web.api.filters import GazetteFilter
from django.contrib.postgres.search import SearchVector
from web.api.serializers import (
    CityCouncilAgendaSerializer,
    CityCouncilAttendanceListSerializer,
    GazetteSerializer,
    CityHallBidSerializer,
)
from web.datasets.models import CityCouncilAgenda, CityCouncilAttendanceList, Gazette, CityHallBid


class HealthCheckView(ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        return Response({"status": "available", "time": datetime.now()})


class CityCouncilAgendaView(ListAPIView):
    queryset = CityCouncilAgenda.objects.all()
    serializer_class = CityCouncilAgendaSerializer

    def get_queryset(self):
        query = self.request.query_params.get("query", None)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        kwargs = {}

        if query:
            kwargs["details__icontains"] = query
        if start_date:
            kwargs["date__gte"] = start_date
        if end_date:
            kwargs["date__lte"] = end_date

        return self.queryset.filter(**kwargs)


class CityCouncilAttendanceListView(ListAPIView):
    queryset = CityCouncilAttendanceList.objects.all()
    serializer_class = CityCouncilAttendanceListSerializer

    def get_queryset(self):
        query = self.request.query_params.get("query", None)
        status = self.request.query_params.get("status", None)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)

        kwargs = {}

        if query:
            kwargs["council_member__icontains"] = query
        if status:
            kwargs["status"] = status
        if start_date:
            kwargs["date__gte"] = start_date
        if end_date:
            kwargs["date__lte"] = end_date

        return self.queryset.filter(**kwargs)


class GazetteView(ReadOnlyModelViewSet):
    queryset = Gazette.objects.all()
    serializer_class = GazetteSerializer
    filterset_class = GazetteFilter
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = [
        "events__title",
        "events__secretariat",
        "events__summary",
        "year_and_edition",
    ]


class CityHallBidView(ListAPIView):
    serializer_class = CityHallBidSerializer

    def get_queryset(self):
        bids = CityHallBid.objects.prefetch_related("events").prefetch_related("files")

        if self.request.query_params:
            bids = self.filter_by_query_params(bids)

        return bids

    def filter_by_query_params(self, bids):
        bids = self.filter_by_query(bids)
        bids = self.filter_by_start_date(bids)
        bids = self.filter_by_end_date(bids)
        return bids

    def filter_by_end_date(self, bids):
        end_date = self.request.query_params.get("end_date", None)
        if end_date is not None:
            bids = bids.filter(session_at__date__lte=end_date)
        return bids

    def filter_by_start_date(self, bids):
        start_date = self.request.query_params.get("start_date", None)
        if start_date is not None:
            bids = bids.filter(session_at__date__gte=start_date)
        return bids

    def filter_by_query(self, bids):
        description = self.request.query_params.get("query", None)

        if description:
            description = description.replace('"', "")
            search_vector = SearchVector("files__search_vector", config="portuguese")
            bids = (
                bids.filter(description__icontains=description)
                | bids.filter(events__summary__icontains=description)
                | bids.annotate(search=search_vector).filter(search=description)
            )
        return bids
