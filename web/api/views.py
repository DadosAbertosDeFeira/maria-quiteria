from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet
from web.api.filters import CityHallBidFilter, GazetteFilter
from web.api.serializers import (
    CityCouncilAgendaSerializer,
    CityCouncilAttendanceListSerializer,
    CityCouncilMinuteSerializer,
    CityHallBidSerializer,
    GazetteSerializer,
)
from web.api.constants import AVAILABLE_ENDPOINTS_BY_PUBLIC_AGENCY
from web.datasets.models import (
    CityCouncilAgenda,
    CityCouncilAttendanceList,
    CityCouncilMinute,
    CityHallBid,
    Gazette,
)


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


class CityCouncilMinuteView(ListAPIView):
    queryset = CityCouncilMinute.objects.all()
    serializer_class = CityCouncilMinuteSerializer

    def get_queryset(self):
        query = self.request.query_params.get("query", None)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        kwargs = {}

        if query:
            kwargs["title__icontains"] = query
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


class CityHallBidView(ListAPIView):
    queryset = CityHallBid.objects.prefetch_related("events").prefetch_related("files")
    serializer_class = CityHallBidSerializer
    filterset_class = CityHallBidFilter
    filter_backends = [SearchFilter, DjangoFilterBackend]


class FrontendEndpoint(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):
        return Response(AVAILABLE_ENDPOINTS_BY_PUBLIC_AGENCY)
