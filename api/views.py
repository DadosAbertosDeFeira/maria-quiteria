from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView
from datasets.models import CityHallBid
from .serializers import CityHallBidSerializer


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "available", "time": datetime.now()})


class CityHallBidView(ListAPIView):
    serializer_class = CityHallBidSerializer

    def get_queryset(self):
        bids = CityHallBid.objects.prefetch_related('events')
        query_params = self.request.query_params

        if query_params:
            bids = self.filter_by_query_params(bids, query_params)

        return bids

    @staticmethod
    def filter_by_query_params(bids, query_params):
        bids = CityHallBidView.filter_by_description(bids, query_params)
        bids = CityHallBidView.filter_by_start_date(bids, query_params)
        bids = CityHallBidView.filter_by_end_date(bids, query_params)
        return bids

    @staticmethod
    def filter_by_end_date(bids, query_params):
        end_date = query_params.get('end_date', None)
        if end_date is not None:
            bids = bids.filter(session_at__lte=end_date)
        return bids

    @staticmethod
    def filter_by_start_date(bids, query_params):
        start_date = query_params.get('start_date', None)
        if start_date is not None:
            bids = bids.filter(session_at__gte=start_date)
        return bids

    @staticmethod
    def filter_by_description(bids, query_params):
        description = query_params.get('query', None)
        if description is not None:
            bids = bids.filter(description__icontains=description) | bids.filter(events__summary__icontains=description)
        return bids
