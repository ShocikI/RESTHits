from rest_framework import viewsets, status
from rest_framework.response import Response

from .utils import generate_title_url
from hits.serializers import (
    ArtistSerializer, Artist,
    HitSerializer, Hit
)

class ArtistViewSet(viewsets.ModelViewSet):
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()


class HitViewSet(viewsets.ModelViewSet):
    serializer_class = HitSerializer
    queryset = Hit.objects.all()
    lookup_field = 'title_url'

    def create(self, request, *args, **kwargs):
        artist_id = request.data.get('artist_id')
        title = request.data.get('title')

        if not artist_id or not title:
            return Response(
                {"detail": "artist_id and title are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            artist = Artist.objects.get(pk=artist_id)
        except Artist.DoesNotExist:
            return Response(
                {"detail": "Unknown artist."}, status=status.HTTP_404_NOT_FOUND    
            )
        
        title_url = generate_title_url(artist, title)

        hit = Hit.objects.create(
            artist_id=artist.id,
            title=title,
            title_url=title_url
        )

        serializer = self.get_serializer(hit)
        return Response(serializer.data, status=status.HTTP_201_CREATED)