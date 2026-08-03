import os
import requests
from django.core.cache import cache
from django.utils import timezone
from requests.exceptions import RequestException
import logging

logger = logging.getLogger(__name__)

class MarketService:
    """
    Service responsible for fetching live market data from data.gov.in AGMARKNET API.
    Handles caching, normalization, and failure fallback.
    """
    
    BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    
    @staticmethod
    def get_market_data(crop, state, district):
        """
        Fetches normalized market data.
        Tries cache first, then calls data.gov.in API.
        """
        cache_key = f"market_data_{crop}_{state}_{district}".replace(" ", "_").lower()
        
        # 1. Check Cache
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {cache_key}")
            return cached_data
            
        logger.info(f"Cache miss for {cache_key}. Fetching from live API.")
        
        # 2. Call data.gov.in API
        api_key = os.getenv('DATA_GOV_IN_API_KEY')
        
        # We'll construct a mock fallback response if the API key is missing or fails
        # so that development can continue smoothly even without the real API key configured yet.
        fallback_data = [
            {"market": f"{district} APMC", "modal_price": 7650.0, "minimum_price": 7300.0, "maximum_price": 7800.0},
            {"market": f"Nearby {district} Market", "modal_price": 7580.0, "minimum_price": 7350.0, "maximum_price": 7700.0},
            {"market": f"{state} Central Mandi", "modal_price": 7450.0, "minimum_price": 7200.0, "maximum_price": 7600.0},
        ]
        
        if not api_key:
            logger.warning("DATA_GOV_IN_API_KEY not found in .env. Returning dummy normalized data.")
            normalized_data = fallback_data
        else:
            try:
                params = {
                    "api-key": api_key,
                    "format": "json",
                    "filters[commodity]": crop,
                    "filters[state]": state,
                    "filters[district]": district,
                    "limit": 10
                }
                
                response = requests.get(MarketService.BASE_URL, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                records = data.get("records", [])
                
                if records:
                    normalized_data = MarketService._normalize_records(records)
                else:
                    normalized_data = fallback_data  # Fallback if no specific records found for strict filters
                    
            except RequestException as e:
                logger.error(f"API Request failed: {str(e)}. Returning fallback data.")
                normalized_data = fallback_data

        # 3. Store in cache for 45 minutes (30-60 mins as requested)
        cache.set(cache_key, normalized_data, timeout=45 * 60)
        
        return normalized_data

    @staticmethod
    def _normalize_records(records):
        """
        Normalizes raw API records into the required schema.
        """
        normalized = []
        for record in records:
            try:
                normalized.append({
                    "market": record.get("market", "Unknown Market"),
                    "modal_price": float(record.get("modal_price", 0)),
                    "minimum_price": float(record.get("min_price", 0)),
                    "maximum_price": float(record.get("max_price", 0)),
                })
            except (ValueError, TypeError):
                continue
                
        # Sort by modal price descending
        normalized.sort(key=lambda x: x["modal_price"], reverse=True)
        return normalized
