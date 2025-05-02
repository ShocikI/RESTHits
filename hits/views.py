from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from .utils import generate_title_url
from hits.serializers import (
    ArtistSerializer, Artist,
    HitSerializer, Hit
)

class ArtistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Artist resources.
    
    Provides CRUD operations for artists with the following endpoints:
    - GET /api/v1/artists/ - List all artists
    - POST /api/v1/artists/ - Create a new artist
    - GET /api/v1/artists/{id}/ - Retrieve a specific artist
    - PUT /api/v1/artists/{id}/ - Update an artist
    - PATCH /api/v1/artists/{id}/ - Partially update an artist
    - DELETE /api/v1/artists/{id}/ - Delete an artist
    
    Attributes:
        serializer_class: The serializer class used for artist data
        queryset: The base queryset for artist objects
    """
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()

    def validate_input(self, data):
        """
        Validate artist input data.
        
        Args:
            data: Dictionary containing artist data
            
        Raises:
            ValidationError: If the data is invalid
        """
        if not data.get('first_name') and not data.get('last_name'):
            raise ValidationError("First_name or last_name is required.")
        
        if len(data.get('first_name', '')) > 32:
            raise ValidationError("First name cannot exceed 32 characters.")
            
        if len(data.get('last_name', '')) > 32:
            raise ValidationError("Last name cannot exceed 32 characters.")

    def create(self, request, *args, **kwargs):
        self.validate_input(request.data)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.validate_input(request.data)
        return super().update(request, *args, **kwargs)


class HitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Hit resources.
    
    Provides CRUD operations for hits with the following endpoints:
    - GET /api/v1/hits/ - List all hits
    - POST /api/v1/hits/ - Create a new hit
    - GET /api/v1/hits/{title_url}/ - Retrieve a specific hit
    - PUT /api/v1/hits/{title_url}/ - Update a hit
    - PATCH /api/v1/hits/{title_url}/ - Partially update a hit
    - DELETE /api/v1/hits/{title_url}/ - Delete a hit
    
    Attributes:
        serializer_class: The serializer class used for hit data
        queryset: The base queryset for hit objects
        lookup_field: The field used for looking up individual hits (title_url)
    """
    serializer_class = HitSerializer
    queryset = Hit.objects.all()
    lookup_field = 'title_url'

    def validate_input(self, data):
        """
        Validate hit input data.
        
        Args:
            data: Dictionary containing hit data
            
        Raises:
            ValidationError: If the data is invalid
        """
        if 'title' in data and len(data['title']) > 128:
            raise ValidationError("Title cannot exceed 128 characters.")
            
        if 'artist_id' in data and not isinstance(data['artist_id'], int):
            raise ValidationError("artist_id must be an integer.")

    def create(self, request, *args, **kwargs):
        """
        Create a new hit.
        
        Args:
            request: The HTTP request object containing:
                - artist_id: ID of the artist who created the hit
                - title: Title of the hit
            
        Returns:
            Response: HTTP response with:
                - 201 Created: Successfully created hit with hit data
                - 400 Bad Request: Missing required fields
                - 404 Not Found: Artist not found
        """
        self.validate_input(request.data)
        
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
        """
        Update an existing hit.
        
        Args:
            request: The HTTP request object containing:
                - artist_id: (optional) New artist ID
                - title: (optional) New title
                - title_url: (optional) New title URL
            title_url: The title_url of the hit to update
            *args: Additional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: HTTP response with:
                - 200 OK: Successfully updated hit with hit data
                - 400 Bad Request: Invalid data
                - 404 Not Found: Hit or artist not found
        """
        self.validate_input(request.data)
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)