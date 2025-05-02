from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

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

        artist = get_object_or_404(Artist, pk=artist_id)
        
        title_url = generate_title_url(artist, title)

        hit = Hit.objects.create(
            artist_id=artist.id,
            title=title,
            title_url=title_url
        )

        serializer = self.get_serializer(hit)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, title_url, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        hit = get_object_or_404(Hit, title_url=title_url)

        artist_id = request.data.get("artist_id")
        if artist_id and artist_id != hit.artist.id:
            artist = get_object_or_404(Artist, pk=artist_id)
        else:
            artist = get_object_or_404(Artist, pk=hit.artist.id)

        title = request.data.get("title")
        if not title:
            title = hit.title

        new_title_url = request.data.get("title_url")
        if not new_title_url:
            new_title_url = hit.title_url

        if new_title_url == hit.title_url:
            new_title_url = generate_title_url(artist, title)

        data = {
            "artist_id": artist.id, 
            "title": title,
            "title_url": new_title_url
        }

        serializer = self.get_serializer(hit, data=data, partial=partial)
        if not serializer.is_valid():
            return Response( serializer.errors, status=status.HTTP_400_BAD_REQUEST )
        
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)