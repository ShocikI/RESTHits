from django.db import models


class Artist(models.Model):
    first_name = models.CharField(max_length=32, blank=False)
    last_name = models.CharField(max_length=32, blank=False)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = ("Artist")
        verbose_name_plural = ("Artists")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Hit(models.Model):
    title = models.CharField(max_length=128, blank=False)
    artist_id = models.ForeignKey(Artist, on_delete=models.CASCADE, blank=False)
    title_url = models.CharField(max_length=256, blank=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = ("Hit")
        verbose_name_plural = ("Hits")

    def __str__(self):
        return f"{self.artist_id.first_name} {self.artist_id.last_name} - {self.title}"
