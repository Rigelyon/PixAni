from django.db import models

class AnimeRecord(models.Model):
    anilist_id = models.IntegerField(unique=True)
    tittle_native = models.CharField(max_length=255)
    tittle_english = models.CharField(max_length=255)
    tittle_romaji = models.CharField(max_length=255)
    anime_type = models.CharField(max_length=50)
    episodes = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50)
    year = models.IntegerField(null=True, blank=True)
    genres = models.CharField(max_length=255, null=True, blank=True)
    synopsis = models.TextField(null=True, blank=True)
    studio = models.CharField(max_length=255, null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)
    cover_image = models.URLField(null=True, blank=True)

    # User data
    personal_rating = models.IntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    download_link_1080p = models.URLField(null=True, blank=True)
    download_link_720p = models.URLField(null=True, blank=True)
    download_link_480p = models.URLField(null=True, blank=True)
    download_link_360p = models.URLField(null=True, blank=True)
    download_link_240p = models.URLField(null=True, blank=True)
    download_link_144p = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tittle_romaji} ({self.year})"
