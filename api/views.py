from datetime import datetime

from datasets.models import CityCouncilAgenda
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CityCouncilAgendaSerializer


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
            kwargs["details__contains"] = query
        if start_date:
            kwargs["date__gte"] = start_date
        if end_date:
            kwargs["date__lte"] = end_date

        return self.queryset.filter(**kwargs)
