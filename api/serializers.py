from rest_framework import serializers

from datasets.models import CityCouncilAgenda, CityCouncilAttendanceList


class CityCouncilAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityCouncilAgenda
        fields = "__all__"


class CityCouncilAttendanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityCouncilAttendanceList
        fields = "__all__"
