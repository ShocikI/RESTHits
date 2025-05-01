from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from hits.models import Artist, Hit
from hits.utils import generate_title_url

class UtilsTestCase(APITestCase):
    def setUp(self):
        self.artist = Artist.objects.create(first_name="Louis", last_name="Armstrong")
    
    def test_generate_title_url_basic(self):
        url = generate_title_url(self.artist, "What A Wonderful World")
        self.assertTrue(url.startswith("louis_armstrong-what_a_wonderful_world_"))
        self.assertTrue(url.endswith("_1") or url.endswith("_2"))

    def test_generate_title_url_increment(self):
        hit_title = "Mega hit"
        title_url_1 = generate_title_url(self.artist, hit_title)
        title_url_2 = generate_title_url(self.artist, hit_title)
    
        Hit.objects.create(artist=self.artist, title=hit_title, title_url=title_url_1)
        Hit.objects.create(artist=self.artist, title=hit_title, title_url=title_url_2)
        url = generate_title_url(self.artist, hit_title)
        self.assertTrue(url.endswith("_3"))

    def test_generate_title_url_unicode_and_spaces(self):
        artist = Artist.objects.create(first_name="Łąó ", last_name=" Ćhę")
        url = generate_title_url(artist, " łabędźi    śpiew  ")
        self.assertIn("lao_che-labedzi_spiew_", url)

    def test_generate_title_url_only_first_name(self):
        artist = Artist.objects.create(first_name="Bob")
        url = generate_title_url(artist, "Long title")
        self.assertTrue(url.startswith("bob-long_title_"))

    def test_generate_title_url_only_last_name(self):
        artist = Artist.objects.create(last_name="Marley")
        url = generate_title_url(artist, "Long title")
        self.assertTrue(url.startswith("marley-long_title_"))
    
    def test_generate_title_url_without_letters(self):
        artist = Artist.objects.create(first_name="';]..,'", last_name=")12(")
        url = generate_title_url(artist, "@#$%!)?")
        self.assertTrue(url.startswith("';]..,'_)12(-@#$%!)?_"))

class ArtistAPITestCase(APITestCase):
    def setUp(self):
        self.artist = Artist.objects.create(first_name="Louis", last_name="Armstrong")
    
    def test_CRUD_artist(self):
        # Create
        get_url = reverse("artist-list")
        data = {"first_name": "Niel", "last_name": "Armstrong"}
        post_response = self.client.post(get_url, data, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", post_response.data)
        artists_counter = Artist.objects.all().count()
        self.assertEqual(artists_counter, 2)
        # Retrieve
        detail_url = reverse("artist-detail", args=[post_response.data["id"]])
        get_response = self.client.get(detail_url, format="json")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data["first_name"], "Niel")
        self.assertEqual(get_response.data["last_name"], "Armstrong")
        # Patch
        patch_response = self.client.patch(detail_url, data={"first_name": "Louis"}, format="json")
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data["first_name"], "Louis")
        self.assertEqual(patch_response.data["last_name"], "Armstrong")
        # Delete
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        artists_counter = Artist.objects.all().count()
        self.assertEqual(artists_counter, 1)

    def test_retrieve_not_existing_artist(self):
        detail_url = reverse("artist-detail", args=[999])
        response = self.client.get(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_patch_not_existing_artist(self):
        detail_url = reverse("artist-detail", args=[999])
        response = self.client.get(detail_url, {"first_name": "Bob"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_artists(self):
        Artist.objects.create(first_name="Bob", last_name="Marley")
        Artist.objects.create(first_name="Sanah")
        list_url = reverse("artist-list")
        response = self.client.get(list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)


class HitAPITestCase(APITestCase):
    def setUp(self):
        self.artist = Artist.objects.create(first_name='Louis', last_name="Armstrong")
        self.list_url = reverse('hit-list')

    def test_create_hit_success(self):
        title_name = "What A Wonderful World"
        data = { "artist_id": self.artist.id, "title": title_name }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], title_name)
        self.assertTrue("title_url" in response.data)

    def test_create_hit_missing_fields(self):
        no_title_data = { "artist_id": self.artist.id }
        response = self.client.post(self.list_url, no_title_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        no_artist_id = { "title": "What A Wonderful World" }
        response = self.client.post(self.list_url, no_artist_id, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_hit_unknown_artist(self):
        data = { "artist_id": 999, "title": "What A Wonderful World" }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_hit_success(self):
        title = "What A Wonderful World"
        title_url = generate_title_url(self.artist, title)
        hit = Hit.objects.create(
            artist=self.artist,
            title=title,
            title_url=title_url
        )
        url = reverse("hit-detail", args=[hit.title_url])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], title)

    def test_retrieve_test_failed(self):
        url = reverse("hit-detail", args=["not_existing_url"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_hits(self):
        title_1 = "Hit1"
        title_2 = "Hit2"
        Hit.objects.create(
            artist=self.artist, title=title_1, 
            title_url=generate_title_url(self.artist, title_1)
        )
        Hit.objects.create(
            artist=self.artist, title=title_2,
            title_url=generate_title_url(self.artist, title_2)
        )
        response = self.client.get(self.list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_patch_fields_hit(self):
        artist = Artist.objects.create(first_name="Sanah")
        original_title = "What A Wonderful World"
        patched_title = "Koronki"
        
        original_url = generate_title_url(self.artist, original_title)
        patched_url = generate_title_url(artist, patched_title)

        hit = Hit.objects.create(
            artist=self.artist,
            title=original_title,
            title_url=original_url
        )
        
        detail_url = reverse("hit-detail", args=[hit.title_url])
        response = self.client.patch(detail_url, data={"artist": artist.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["artist_id"], artist.id)

        response = self.client.patch(detail_url, data={"title": patched_title}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], patched_title)

        response = self.client.patch(detail_url, data={"title_url": patched_url}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title_url"], patched_url)

    def test_delete_hit(self):
        hit = Hit.objects.create(
            artist=self.artist,
            title="Koronki",
            title_url="very_long_url"
        )
        detail_url = reverse("hit-detail", args=[hit.title_url])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_delete_not_existing_hit(self):
        detail_url = reverse("hit-detail", args=["not_existing_url"])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


