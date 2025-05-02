from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from hits.models import Artist, Hit
from hits.utils import generate_title_url

class UtilsTestCase(APITestCase):
    """Test cases for utility functions."""
    
    def setUp(self):
        self.artist = Artist.objects.create(first_name="Louis", last_name="Armstrong")
    
    def test_generate_title_url_basic(self):
        """Test basic title URL generation."""
        url = generate_title_url(self.artist, "What A Wonderful World")
        self.assertTrue(url.startswith("louis_armstrong-what_a_wonderful_world"))
        # The URL should not end with a counter if it's unique
        self.assertFalse(url.endswith("_1") or url.endswith("_2"))

    def test_generate_title_url_increment(self):
        """Test title URL generation with multiple hits."""
        hit_title = "Mega hit"
        title_url_1 = generate_title_url(self.artist, hit_title)
    
        # Create first hit
        Hit.objects.create(artist=self.artist, title=hit_title, title_url=title_url_1)
        
        # Create second hit with the same title
        url = generate_title_url(self.artist, hit_title)
        self.assertTrue(url.endswith("_1"))  # Should append _1 for the first duplicate
        
        # Create the second hit
        Hit.objects.create(artist=self.artist, title=hit_title, title_url=url)
        
        # Try to create another hit with the same title
        url = generate_title_url(self.artist, hit_title)
        self.assertTrue(url.endswith("_2"))  # Should append _2 for the second duplicate

    def test_generate_title_url_unicode_and_spaces(self):
        """Test title URL generation with Unicode characters and spaces."""
        artist = Artist.objects.create(first_name="Łąó ", last_name=" Ćhę")
        url = generate_title_url(artist, " łabędźi    śpiew  ")
        self.assertIn("lao_che-labedzi_spiew", url)

    def test_generate_title_url_only_first_name(self):
        """Test title URL generation with only first name."""
        artist = Artist.objects.create(first_name="Bob")
        url = generate_title_url(artist, "Long title")
        self.assertTrue(url.startswith("bob-long_title"))

    def test_generate_title_url_only_last_name(self):
        """Test title URL generation with only last name."""
        artist = Artist.objects.create(last_name="Marley")
        url = generate_title_url(artist, "Long title")
        self.assertTrue(url.startswith("marley-long_title"))
    
    def test_generate_title_url_without_letters(self):
        """Test title URL generation with special characters."""
        artist = Artist.objects.create(first_name="';]..,'", last_name=")12(")
        url = generate_title_url(artist, "@#$%!)?")
        self.assertTrue(url.startswith("';]..,'_)12(-@#$%!)?"))

    def test_generate_title_url_max_length(self):
        """Test title URL generation with maximum length fields."""
        long_name = "a" * 32
        long_title = "b" * 128
        artist = Artist.objects.create(first_name=long_name, last_name=long_name)
        url = generate_title_url(artist, long_title)
        self.assertLessEqual(len(url), 256)  # title_url field max length


class ArtistAPITestCase(APITestCase):
    """Test cases for Artist API endpoints."""
    
    def setUp(self):
        self.artist = Artist.objects.create(first_name="Louis", last_name="Armstrong")
        self.list_url = reverse("artist-list")
    
    def test_CRUD_artist(self):
        """Test complete CRUD operations for artists."""
        # Create
        data = {"first_name": "Niel", "last_name": "Armstrong"}
        post_response = self.client.post(self.list_url, data, format="json")
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

        # Update
        patch_response = self.client.patch(detail_url, data={"first_name": "Louis"}, format="json")
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data["first_name"], "Louis")
        self.assertEqual(patch_response.data["last_name"], "Armstrong")

        # Delete
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        artists_counter = Artist.objects.all().count()
        self.assertEqual(artists_counter, 1)

    def test_create_artist_validation(self):
        """Test artist creation with invalid data."""
        # Missing required fields
        data = {"first_name": "John"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Field length validation
        data = {"first_name": "a" * 33, "last_name": "Doe"}  # Exceeds max_length
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_not_existing_artist(self):
        """Test retrieving non-existent artist."""
        detail_url = reverse("artist-detail", args=[999])
        response = self.client.get(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_patch_not_existing_artist(self):
        """Test updating non-existent artist."""
        detail_url = reverse("artist-detail", args=[999])
        response = self.client.patch(detail_url, {"first_name": "Bob"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_artists(self):
        """Test listing all artists."""
        Artist.objects.create(first_name="Bob", last_name="Marley")
        Artist.objects.create(first_name="Sanah")
        response = self.client.get(self.list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)

    def test_list_artists_ordering(self):
        """Test artist list ordering by creation date."""
        Artist.objects.create(first_name="Bob", last_name="Marley")
        Artist.objects.create(first_name="Sanah")
        response = self.client.get(self.list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if artists are ordered by created_at
        artists = response.data.get('results', response.data)  # Handle both paginated and non-paginated responses
        for i in range(len(artists) - 1):
            self.assertLessEqual(
                artists[i]['created_at'],
                artists[i + 1]['created_at']
            )


class HitAPITestCase(APITestCase):
    """Test cases for Hit API endpoints."""
    
    def setUp(self):
        self.artist = Artist.objects.create(first_name='Louis', last_name="Armstrong")
        self.list_url = reverse('hit-list')

    def test_create_hit_success(self):
        """Test successful hit creation."""
        title_name = "What A Wonderful World"
        data = { "artist_id": self.artist.id, "title": title_name }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], title_name)
        self.assertTrue("title_url" in response.data)

    def test_create_hit_validation(self):
        """Test hit creation with invalid data."""
        # Missing required fields
        no_title_data = { "artist_id": self.artist.id }
        response = self.client.post(self.list_url, no_title_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        no_artist_id = { "title": "What A Wonderful World" }
        response = self.client.post(self.list_url, no_artist_id, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid artist_id
        data = { "artist_id": "not_an_id", "title": "What A Wonderful World" }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Title length validation
        data = { "artist_id": self.artist.id, "title": "a" * 129 }  # Exceeds max_length
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_hit_unknown_artist(self):
        """Test hit creation with non-existent artist."""
        data = { "artist_id": 999, "title": "What A Wonderful World" }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_empty_hit(self):
        """Test hit creation with empty data."""
        data = {}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = { "artist_id": "", "title": "" }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_hit_success(self):
        """Test successful hit retrieval."""
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

    def test_retrieve_hit_not_existing(self):
        """Test retrieving non-existent hit."""
        url = reverse("hit-detail", args=["not_existing_url"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_hits(self):
        """Test listing all hits."""
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

    def test_list_hits_ordering(self):
        """Test hit list ordering by creation date."""
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
        # Check if hits are ordered by created_at in descending order
        hits = response.data.get('results', response.data)  # Handle both paginated and non-paginated responses
        for i in range(len(hits) - 1):
            self.assertGreaterEqual(
                hits[i]['created_at'],
                hits[i + 1]['created_at']
            )

    def test_patch_hit(self):
        """Test partial hit update."""
        artist = Artist.objects.create(first_name="Sanah")
        hit = Hit.objects.create(
            artist=self.artist,
            title="What A Wonderful World",
            title_url=generate_title_url(self.artist, "What A Wonderful World")
        )
        detail_url = reverse("hit-detail", args=[hit.title_url])
        
        # Update artist
        new_url = generate_title_url(artist, hit.title)
        response = self.client.patch(
            detail_url, data={ "artist_id": artist.id }, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["artist_id"], artist.id)
        self.assertEqual(response.data["title_url"], new_url)
        
        # Update title
        detail_url = reverse("hit-detail", args=[new_url])
        new_title = "New hit"
        new_url = generate_title_url(artist, new_title)
        response = self.client.patch(detail_url, data={"title": new_title}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], new_title)
        self.assertEqual(response.data["title_url"], new_url)
        
        # Update title_url
        detail_url = reverse("hit-detail", args=[new_url])
        response = self.client.patch(detail_url, data={"title_url": "long_url"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title_url"], "long_url")
    
    def test_put_hit(self):
        """Test complete hit update."""
        artist = Artist.objects.create(first_name="Sanah")
        hit = Hit.objects.create(
            artist=self.artist,
            title="What A Wonderful World",
            title_url=generate_title_url(self.artist, "What A Wonderful World")
        )
        detail_url = reverse("hit-detail", args=[hit.title_url])
        new_url = "long_url"
        response = self.client.put(
            detail_url, 
            data={ 
                "artist_id": artist.id,
                "title": "Koronki",
                "title_url": new_url
            }, 
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["artist_id"], artist.id)
        self.assertEqual(response.data["title"], "Koronki")
        self.assertEqual(response.data["title_url"], new_url)

    def test_patch_hit_not_existing(self):
        """Test updating non-existent hit."""
        artist = Artist.objects.create(first_name="Sanah")
        detail_url = reverse("hit-detail", args=["not_existing_url"])
        response = self.client.patch(
            detail_url, 
            data={ 
                "artist_id": artist.id,
                "title": "Koronki",
                "title_url": "some_new_url"
            }, 
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_hit(self):
        """Test hit deletion."""
        hit = Hit.objects.create(
            artist=self.artist,
            title="Koronki",
            title_url="very_long_url"
        )
        detail_url = reverse("hit-detail", args=[hit.title_url])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Hit.objects.filter(title_url=hit.title_url).exists())

    def test_delete_hit_not_existing(self):
        """Test deleting non-existent hit."""
        detail_url = reverse("hit-detail", args=["not_existing_url"])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


