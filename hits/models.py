from django.db import models


class Artist(models.Model):
    first_name = models.CharField(max_length=32, blank=False)
    last_name = models.CharField(max_length=32, blank=False)
    created_at = models.DateField(auto_now_add=True)


class Hit(models.Model):
    title = models.CharField(max_length=128, blank=False)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, blank=False)
    title_url = models.CharField(max_length=256, blank=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

