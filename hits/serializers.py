from rest_framework import serializers

from hits.models import Artist, Hit


class ArtistSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'first_name', 'last_name', 'created_at']

class HitSerializer(serializers.HyperlinkedModelSerializer):
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all()
    )

    class Meta:
        model = Hit
        fields = ['title', 'artist_id', 'title', 'title_url', 'created_at', 'updated_at']
        read_only_fields = ["created_at", "updated_at"]

    