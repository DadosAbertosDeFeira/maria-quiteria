from rest_framework import serializers
from datasets.models import CityHallBid, CityHallBidEvent, File, CityCouncilAgenda


class CityCouncilAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityCouncilAgenda
        fields = "__all__"


class CityHallBidEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityHallBidEvent
        fields = '__all__'


class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['url'] # TODO: verificar se content deve ser retornado também


class CityHallBidSerializer(serializers.ModelSerializer):

    events = CityHallBidEventSerializer(many=True, read_only=True)
    files = FilesSerializer(many=True, read_only=True)

    class Meta:
        model = CityHallBid
        fields = '__all__'
