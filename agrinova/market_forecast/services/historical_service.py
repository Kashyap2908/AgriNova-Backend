import os
import requests
import logging
from datetime import datetime, timedelta
from django.core.cache import cache

logger = logging.getLogger(__name__)

class HistoricalMarketService:
    BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    
    @staticmethod
    def get_historical_data(crop, state, district, days=30):
        """
        Fetches bulk historical market data from data.gov.in.
        Since we cannot pass a pure date range easily without exhausting limits,
        we fetch up to a large limit and filter by date locally, or we accept whatever
        historical records the API returns for that crop/state.
        """
        cache_key = f"historical_data_{crop}_{state}_{district}_{days}".replace(" ", "_").lower()
        
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Historical Cache hit for {cache_key}")
            return cached_data
            
        logger.info(f"Historical Cache miss for {cache_key}. Fetching from API.")
        
        api_key = os.getenv('DATA_GOV_IN_API_KEY')
        if not api_key:
            logger.warning("DATA_GOV_IN_API_KEY missing. Generating realistic mock historical data for UI preview.")
            records = HistoricalMarketService._generate_mock_data(crop, state, district, days)
            cache.set(cache_key, records, timeout=24 * 60 * 60)
            return records
            
        records = []
        try:
            params = {
                "api-key": api_key,
                "format": "json",
                "filters[commodity]": crop,
                "filters[state]": state,
                "limit": 5000, # Fetch a large bulk to get history
            }
            if district and district.lower() != 'all':
                params["filters[district]"] = district
                
            response = requests.get(HistoricalMarketService.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            raw_records = data.get("records", [])
            
            # Parse dates and filter by requested days
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for record in raw_records:
                arrival_date_str = record.get("arrival_date")
                if not arrival_date_str:
                    continue
                    
                try:
                    # Format is usually dd/mm/yyyy
                    arrival_date = datetime.strptime(arrival_date_str, "%d/%m/%Y")
                    if arrival_date >= cutoff_date:
                        records.append({
                            "date": arrival_date.strftime("%Y-%m-%d"),
                            "market": record.get("market", "Unknown"),
                            "commodity": record.get("commodity", crop),
                            "modal_price": float(record.get("modal_price", 0)),
                            "minimum_price": float(record.get("min_price", 0)),
                            "maximum_price": float(record.get("max_price", 0)),
                            "arrival_quantity": float(record.get("arrival", 0)) if "arrival" in record else 0.0,
                        })
                except (ValueError, TypeError):
                    continue
                    
            # Sort chronologically
            records.sort(key=lambda x: x["date"])
            
            if not records:
                logger.warning(f"API returned 0 valid historical records for {crop} in {state}. Generating mock data for UI preview.")
                records = HistoricalMarketService._generate_mock_data(crop, state, district, days)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Historical API Request failed: {e}")
            logger.warning("Generating realistic mock historical data due to API failure.")
            records = HistoricalMarketService._generate_mock_data(crop, state, district, days)
            
        # Cache for 24 hours
        cache.set(cache_key, records, timeout=24 * 60 * 60)
        return records

    @staticmethod
    def _generate_mock_data(crop, state, district, days):
        """Generates realistic mock historical data when API is unavailable."""
        import random
        mock_records = []
        base_price = 7500.0
        markets = [f"{district} APMC", f"Nearby {district}", f"{state} Central"] if district != "all" else [f"{state} Market 1", f"{state} Market 2"]
        
        for i in range(days):
            date_str = (datetime.now() - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
            # Create some volatility
            daily_variation = random.uniform(-200, 200)
            trend = (i / days) * 300  # Slight upward trend
            current_base = base_price + daily_variation + trend
            
            for m in markets:
                market_variation = random.uniform(-50, 50)
                modal = round(current_base + market_variation, 2)
                mock_records.append({
                    "date": date_str,
                    "market": m,
                    "commodity": crop,
                    "modal_price": modal,
                    "minimum_price": round(modal * 0.95, 2),
                    "maximum_price": round(modal * 1.05, 2),
                    "arrival_quantity": round(random.uniform(50, 300), 2),
                    "is_mock": True
                })
        return mock_records

