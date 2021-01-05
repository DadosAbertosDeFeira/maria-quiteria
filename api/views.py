from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView
from datasets.models import CityHallBid, CityHallBidEvent
from .serializers import CityHallBidSerializer


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "available", "time": datetime.now()})


class CityHallBidView(ListAPIView):
    serializer_class = CityHallBidSerializer

    def get_queryset(self):
        bids = CityHallBid.objects.all()
        events = CityHallBidEvent.objects.all()

        description = self.request.query_params.get('description', None)

        if description is not None:
            bids = bids.filter(description__contains=description)
            events = events.filter(summary__contains=description)
            bids = bids.filter(events__in=events)

        return bids
