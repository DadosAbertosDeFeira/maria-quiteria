from datasets.models import CityCouncilAgenda, CityHallBid, CityHallBidEvent, File
from rest_framework import serializers


class CityCouncilAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityCouncilAgenda
        fields = "__all__"


class CityHallBidEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityHallBidEvent
        fields = "__all__"


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["url"]


class CityHallBidSerializer(serializers.ModelSerializer):

    events = CityHallBidEventSerializer(many=True, read_only=True)
    files = FilesSerializer(many=True, read_only=True)

    class Meta:
        model = CityHallBid
        fields = "__all__"
