from rest_framework import serializers

from hits.models import Artist, Hit


class ArtistSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        """Meta options for ArtistSerializer."""
        model = Artist
        fields = ['id', 'first_name', 'last_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class HitSerializer(serializers.ModelSerializer):
    """Serializer for the Hit model."""
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(), 
        source="artist"
    )
    
    class Meta:
        """Meta options for HitSerializer."""
        model = Hit
        fields = ['title', 'artist_id', 'title', 'title_url', 'created_at', 'updated_at']
        read_only_fields = ["created_at", "updated_at"]

    