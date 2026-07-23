import requests
import logging

logger = logging.getLogger(__name__)

def fetch_coordinates_nominatim(village, taluka, district, state):
    """
    Asynchronously or inline fetches geographical coordinates from OpenStreetMap Nominatim API.
    Returns (latitude, longitude) as floats, or (None, None) gracefully on timeout or failure.
    """
    try:
        parts = [p.strip() for p in [village, taluka, district, state, 'India'] if p and str(p).strip()]
        query = ", ".join(parts)

        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': query,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'AgriNova-Backend/1.0 (contact@agrinova.com)'
        }

        response = requests.get(url, params=params, headers=headers, timeout=4)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                lat = float(data[0].get('lat'))
                lon = float(data[0].get('lon'))
                return lat, lon

        # Fallback to broader query (district, state) if village-specific lookup yields no results
        if village:
            broader_parts = [p.strip() for p in [district, state, 'India'] if p and str(p).strip()]
            broader_query = ", ".join(broader_parts)
            response = requests.get(url, params={'q': broader_query, 'format': 'json', 'limit': 1}, headers=headers, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return float(data[0].get('lat')), float(data[0].get('lon'))

    except Exception as e:
        logger.warning(f"Nominatim geocoding lookup failed for query '{village}, {district}, {state}': {e}")
    
    return None, None
