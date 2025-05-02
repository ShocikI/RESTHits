from django.db import models


class Artist(models.Model):
    """
    Represents a musical artist in the system.
    
    Attributes:
        first_name (str): The artist's first name. Required, max length 32 characters.
        last_name (str): The artist's last name. Required, max length 32 characters.
        created_at (date): The date when the artist was added to the system. Automatically set.
    """
    first_name = models.CharField(max_length=32, blank=False)
    last_name = models.CharField(max_length=32, blank=False)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        """
        Metadata options for the Artist model.
        
        Attributes:
            ordering (list): Specifies the default ordering of artists by creation date.
        """
        ordering = ['created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Hit(models.Model):
    """
    Represents a hit song in the system.
    
    Attributes:
        title (str): The title of the hit song. Required, max length 128 characters.
        artist (Artist): The artist who created this hit. Required, foreign key to Artist model.
        title_url (str): A unique URL-friendly slug for the hit. Required, max length 256 characters.
        created_at (date): The date when the hit was added to the system. Automatically set.
        updated_at (date): The date when the hit was last modified. Automatically updated.
    """
    title = models.CharField(max_length=128, blank=False)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, blank=False)
    title_url = models.CharField(max_length=256, blank=False, unique=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        """
        Metadata options for the Hit model.
        
        Attributes:
            ordering (list): Specifies the default ordering of hits by creation date in descending order.
        """
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.artist.first_name} {self.artist.last_name} - {self.title}"
