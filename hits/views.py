from rest_framework import viewsets

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

