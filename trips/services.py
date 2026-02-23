import requests
from django.core.cache import cache
from django.conf import settings


class AICServiceError(Exception):
    pass


class AICService:
    BASE_URL = settings.AIC_BASE_URL
    FIELDS = "id,title,artist_display,image_id"
    IIIF_BASE = "https://www.artic.edu/iiif/2"

    def get_artwork(self, artwork_id: int) -> dict:
        cache_key = f"aic_artwork_{artwork_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        url = f"{self.BASE_URL}/artworks/{artwork_id}"
        try:
            response = requests.get(url, params={"fields": self.FIELDS}, timeout=10)
        except requests.RequestException as e:
            raise AICServiceError(f"Failed to connect to Art Institute of Chicago API: {e}")

        if response.status_code == 404:
            raise AICServiceError(f"Artwork with ID {artwork_id} not found in the Art Institute of Chicago API.")
        if not response.ok:
            raise AICServiceError(f"Art Institute of Chicago API returned status {response.status_code}.")

        data = response.json().get("data", {})

        image_id = data.get("image_id")
        image_url = f"{self.IIIF_BASE}/{image_id}/full/843,/0/default.jpg" if image_id else ""

        result = {
            "id": data["id"],
            "title": data.get("title", "Unknown"),
            "artist_display": data.get("artist_display", ""),
            "image_url": image_url,
        }

        cache.set(cache_key, result, timeout=settings.AIC_CACHE_TIMEOUT)
        return result
