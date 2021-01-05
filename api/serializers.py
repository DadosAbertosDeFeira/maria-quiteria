from datasets.models import CityCouncilAgenda
from rest_framework import serializers


class CityCouncilAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityCouncilAgenda
        fields = "__all__"
