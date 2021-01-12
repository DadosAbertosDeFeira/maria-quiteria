from datetime import datetime

from datasets.models import CityCouncilAgenda, CityHallBid
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CityCouncilAgendaSerializer, CityHallBidSerializer


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
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

            bids = (
                bids.filter(description__icontains=description)
                | bids.filter(events__summary__icontains=description)
                | bids.filter(files__search_vector__icontains=description)
            )
        return bids
