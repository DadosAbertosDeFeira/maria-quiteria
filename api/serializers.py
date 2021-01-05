from rest_framework import serializers
from datasets.models import CityHallBid, CityHallBidEvent


class CityHallBidEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityHallBidEvent
        fields = '__all__'


class CityHallBidSerializer(serializers.ModelSerializer):

    events = CityHallBidEventSerializer(many=True, read_only=True)

    class Meta:
        model = CityHallBid
        fields = '__all__'
