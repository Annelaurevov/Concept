import os
from dotenv import load_dotenv

# Laad .env bestand
load_dotenv()


class Config:
    # Unsplash configuratie
    UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"
    UNSPLASH_RANDOM_URL = "https://api.unsplash.com/photos/random"
    UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY", "fallback_unsplash_key")
    UNSPLASH_DEFAULT_QUERY = os.getenv("UNSPLASH_DEFAULT_QUERY", "christmas")

    # Rijksmuseum configuratie
    RIJKSMUSEUM_API_URL = "https://www.rijksmuseum.nl/api/en/collection"
    RIJKSMUSEUM_API_KEY = os.getenv("RIJKSMUSEUM_API_KEY",
                                    "fallback_rijksmuseum_key")

    # Edamam configuratie
    EDAMAM_API_URL = "https://api.edamam.com/search"
    EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID", "fallback_edamam_id")
    EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY", "fallback_edamam_key")
