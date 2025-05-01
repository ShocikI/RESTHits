from django.urls import re_path, include
from rest_framework.routers import DefaultRouter

from hits.views import HitViewSet, ArtistViewSet


router = DefaultRouter()
router.register(r'hits', HitViewSet, basename="hit")
router.register(r'artists', ArtistViewSet, basename="artist")

urlpatterns = [
    re_path(r'^', include(router.urls))
]