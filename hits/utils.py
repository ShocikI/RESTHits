from unidecode import unidecode
from re import sub

from .models import Artist, Hit

def generate_title_url(artist: Artist, title: str):
    title_url = ""

    clean_first_name = sub(r'\s+', '_', unidecode(artist.first_name.strip().lower()))
    clean_last_name = sub(r'\s+', '_', unidecode(artist.last_name.strip().lower()))
    clean_title = sub(r'\s+', '_', unidecode(title.strip().lower()))

    if clean_first_name != "" and clean_last_name != "":
        clean_last_name = f"_{clean_last_name}"
    
    title_url = f"{clean_first_name}{clean_last_name}-{clean_title}"
    titles_counter = 1

    repetitions = Hit.objects.filter(artist_id=artist.id, title=title).count()
    titles_counter += repetitions

    return f"{title_url}_{titles_counter}"