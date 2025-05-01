from django.core.management.base import BaseCommand
from hits.models import Artist, Hit
from hits.utils import generate_title_url

class Command(BaseCommand):
    help = "Seed initial artists and hits data into the database"
    artists_data = [
        { "first_name": "Dawid", "last_name": "Podsiadło" },
        { "first_name": "Sanah", "last_name": "" },
        { "first_name": "Daria", "last_name": "Zawiałow" },
        { "first_name": "Guzior", "last_name": "" },
        { "first_name": "Łona", "last_name": "" }
    ]

    hits_data = [
        {"artist_id": 0, "title": "Cantate Tutti"},
        {"artist_id": 0, "title": "No"},
        {"artist_id": 0, "title": "Trofea"},
        {"artist_id": 0, "title": "Pastempomat"},
        {"artist_id": 0, "title": "Wirus"},
        {"artist_id": 0, "title": "Post"},
        {"artist_id": 0, "title": "Forest"},
        {"artist_id": 0, "title": "mori"},
        {"artist_id": 0, "title": "Nieznajomy"},
        {"artist_id": 0, "title": "Małomiasteczkowy"},
        {"artist_id": 1, "title": "Szampan"},
        {"artist_id": 1, "title": "Melodia"},
        {"artist_id": 1, "title": "Ale jazz"},
        {"artist_id": 1, "title": "etc."},
        {"artist_id": 1, "title": "ten Stan"},
        {"artist_id": 1, "title": "było, minęło"},
        {"artist_id": 1, "title": "Nic dwa razy"},
        {"artist_id": 1, "title": "Co ja robię tutaj"},
        {"artist_id": 1, "title": "2/10"},
        {"artist_id": 1, "title": "Warcaby"},
        {"artist_id": 2, "title": "Złamane serce jest OK"},
        {"artist_id": 2, "title": "Ballada o Niej"},
        {"artist_id": 2, "title": "Dziwna"},
        {"artist_id": 2, "title": "SUPRO"},
        {"artist_id": 2, "title": "Z Tobą na chacie"},
        {"artist_id": 2, "title": "FIFI HOLLYWOOD"},
        {"artist_id": 2, "title": "Laura"},
        {"artist_id": 2, "title": "Szarówka"},
        {"artist_id": 2, "title": "Hej Hej!"},
        {"artist_id": 2, "title": "Dziewczyna Pop"},
        {"artist_id": 3, "title": "BLUEBERRY"},
        {"artist_id": 3, "title": "FALA"},
        {"artist_id": 3, "title": "STRZELAM PETEM"},
        {"artist_id": 3, "title": "WIFI"},
        {"artist_id": 3, "title": "HILL BOMB"},
        {"artist_id": 3, "title": "KUSHKOMA"},
        {"artist_id": 3, "title": "KUSHKOMA"},
        {"artist_id": 3, "title": "Ninja"},
        {"artist_id": 3, "title": "BOILER ROOM"},
        {"artist_id": 3, "title": "CASTROL"},
        {"artist_id": 4, "title": "To Nic Nie Znaczy"},
        {"artist_id": 4, "title": "Błąd"},
        {"artist_id": 4, "title": "PAN DAREK"},
        {"artist_id": 4, "title": "Rozmowa"},
        {"artist_id": 4, "title": "KOCYK"},
        {"artist_id": 4, "title": "Miej wątpliwość"},
        {"artist_id": 4, "title": "10 PYTAŃ"},
        {"artist_id": 4, "title": "BYM POSZEDŁ"},
        {"artist_id": 4, "title": "Wyślij Sobie Pocztówkę"},
        {"artist_id": 4, "title": "Patrz Szerzej"},
    ]

    def handle(self, *args, **kwargs):
        if Artist.objects.exists() and Hit.objects.exists():
            self.stdout.write("Data have been already mocked.")
            return
        
        artists = []
        for data in self.artists_data:
            artist = Artist.objects.create( 
                first_name=data["first_name"],
                last_name=data["last_name"]
            )
            artists.append(artist)

        for data in self.hits_data:
            artist = artists[data["artist_id"]]
            title = data["title"]

            title_url = generate_title_url(artist, title)

            Hit.objects.create( 
                title=title,
                artist=artist,
                title_url=title_url
            )

        self.stdout.write(
            self.style.SUCCESS("Data have been added to database.")
        )
        