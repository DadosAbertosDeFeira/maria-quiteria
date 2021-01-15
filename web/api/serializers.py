from rest_framework import serializers

from web.datasets.models import CityCouncilAgenda


class CityCouncilAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityCouncilAgenda
        fields = "__all__"
