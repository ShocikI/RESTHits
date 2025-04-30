from rest_framework import serializers

from hits.models import Artist, Hit


class ArtistSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'

class HitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Hit
        fields = '__all__'

    