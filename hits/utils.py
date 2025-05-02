from unidecode import unidecode
from re import sub

from .models import Artist, Hit

def generate_title_url(artist: Artist, title: str) -> str:
    """
    Generate a unique URL-friendly slug for a hit song.
    
    Args:
        artist: The Artist instance
        title: The title of the hit song
        
    Returns:
        A unique URL-friendly string in the format: firstname_lastname-title_counter
    """
    # Clean and normalize the components
    clean_first_name = sub(r'\s+', '_', unidecode(artist.first_name.strip().lower()))
    clean_last_name = sub(r'\s+', '_', unidecode(artist.last_name.strip().lower()))
    clean_title = sub(r'\s+', '_', unidecode(title.strip().lower()))

    # Build the base URL
    if clean_first_name and clean_last_name:
        base_url = f"{clean_first_name}_{clean_last_name}-{clean_title}"
    else:
        base_url = f"{clean_first_name}{clean_last_name}-{clean_title}"

    # Start with the base URL
    title_url = base_url
    counter = 1

    # Keep incrementing the counter until we find a unique URL
    while Hit.objects.filter(title_url=title_url).exists():
        title_url = f"{base_url}_{counter}"
        counter += 1

    return title_url