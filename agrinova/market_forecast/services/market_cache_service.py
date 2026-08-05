import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction

# pyrefly: ignore [missing-import]
from ..models import MarketCache
from .market_service import MarketService
from .historical_service import HistoricalMarketService

logger = logging.getLogger(__name__)

class MarketCacheService:
    """
    Service managing MarketCache records.
    Provides:
    - Lazy cache checks and live API fetching
    - Daily current price caching
    - 24h history updates for 7-day (weekly), 30-day (monthly), and 365-day (yearly) history
    - Automatic rolling window history rotation
    - Retraining triggers for ML prediction models
    """

    @staticmethod
    def get_or_fetch_market_cache(crop: str, state: str, district: str, market: str = None) -> MarketCache:
        """
        Retrieves or fetches MarketCache for the given (crop, state, district, market).
        If market is not provided, defaults to '{district} APMC'.
        """
        crop_clean = crop.strip()
        state_clean = state.strip()
        district_clean = district.strip()
        market_clean = market.strip() if market else f"{district_clean} APMC"

        today_str = timezone.now().strftime("%Y-%m-%d")

        cache, created = MarketCache.objects.get_or_create(
            crop=crop_clean,
            state=state_clean,
            district=district_clean,
            market=market_clean
        )

        # Check if today's current price is already cached
        today_price_exists = False
        if not created and cache.current_price:
            last_updated_date = cache.current_price.get("last_updated") or (
                cache.last_updated.strftime("%Y-%m-%d") if cache.last_updated else None
            )
            if last_updated_date == today_str:
                today_price_exists = True

        new_history_added = False

        # If today's price does not exist or history is empty, fetch live market data
        if not today_price_exists or not cache.weekly_price_history:
            live_records = MarketService.get_market_data(crop_clean, state_clean, district_clean)
            
            # Find matching market or use top market
            target_record = None
            for rec in live_records:
                if rec.get("market", "").lower() == market_clean.lower():
                    target_record = rec
                    break
            if not target_record and live_records:
                target_record = live_records[0]
                if target_record.get("market"):
                    market_clean = target_record.get("market")

            if target_record:
                modal_price = float(target_record.get("modal_price", 0))
                min_price = float(target_record.get("minimum_price", modal_price * 0.95))
                max_price = float(target_record.get("maximum_price", modal_price * 1.05))

                cache.current_price = {
                    "crop": crop_clean,
                    "state": state_clean,
                    "district": district_clean,
                    "market": market_clean,
                    "minimum_price": min_price,
                    "modal_price": modal_price,
                    "maximum_price": max_price,
                    "arrival_quantity": target_record.get("arrival_quantity", 100.0),
                    "last_updated": today_str
                }

                # Populate initial historical data if history is empty
                if not cache.weekly_price_history or not cache.monthly_price_history or not cache.yearly_price_history:
                    new_history_added = MarketCacheService._initialize_historical_cache(cache, crop_clean, state_clean, district_clean)

                # Update history records with today's price if not present today
                new_history_added = MarketCacheService._append_today_price_and_rotate(
                    cache, today_str, min_price, modal_price, max_price
                ) or new_history_added

                cache.save()

        # Trigger ML model update if new historical data was added
        if new_history_added:
            MarketCacheService._notify_model_retrain()

        return cache

    @staticmethod
    def _initialize_historical_cache(cache: MarketCache, crop: str, state: str, district: str) -> bool:
        """Populates 365-day historical records from HistoricalMarketService if empty."""
        hist_records = HistoricalMarketService.get_historical_data(crop, state, district, days=365)
        if not hist_records:
            return False

        is_mock = any(r.get("is_mock", False) for r in hist_records)

        # Sort chronologically by date
        sorted_records = sorted(hist_records, key=lambda x: x.get("date", ""))
        
        yearly_list = []
        for r in sorted_records:
            item = {
                "date": r.get("date"),
                "min_price": float(r.get("minimum_price", 0)),
                "modal_price": float(r.get("modal_price", 0)),
                "max_price": float(r.get("maximum_price", 0))
            }
            if not any(existing["date"] == item["date"] for existing in yearly_list):
                yearly_list.append(item)

        cache.yearly_price_history = yearly_list[-365:]
        cache.monthly_price_history = yearly_list[-30:]
        cache.weekly_price_history = yearly_list[-7:]

        # Retrain model ONLY if REAL (non-mock) historical data was fetched
        return not is_mock

    @staticmethod
    def _append_today_price_and_rotate(cache: MarketCache, today_str: str, min_p: float, modal_p: float, max_p: float) -> bool:
        """
        Appends today's price to weekly, monthly, and yearly price histories without creating duplicates.
        Applies strict rolling automatic rotation limits:
        - weekly_price_history: max 7 items
        - monthly_price_history: max 30 items
        - yearly_price_history: max 365 items
        """
        today_entry = {
            "date": today_str,
            "min_price": min_p,
            "modal_price": modal_p,
            "max_price": max_p
        }

        history_changed = False

        for attr, max_len in [
            ("weekly_price_history", 7),
            ("monthly_price_history", 30),
            ("yearly_price_history", 365)
        ]:
            history = list(getattr(cache, attr, []) or [])
            # Check if today's record already exists
            existing_idx = next((i for i, item in enumerate(history) if item.get("date") == today_str), None)

            if existing_idx is not None:
                # Update existing record
                history[existing_idx] = today_entry
            else:
                # Append new record
                history.append(today_entry)
                history_changed = True

            # Sort by date ascending
            history.sort(key=lambda x: x.get("date", ""))

            # Enforce strict rolling rotation limit (remove oldest entries if len > max_len)
            if len(history) > max_len:
                history = history[-max_len:]
                history_changed = True

            setattr(cache, attr, history)

        return history_changed

    @staticmethod
    def _notify_model_retrain():
        """Notifies MarketModelManager to train/retrain prediction model when new data is added."""
        try:
            from ml.market_model_manager import MarketModelManager
            MarketModelManager.get_instance().check_and_retrain(force=True)
        except Exception as e:
            logger.warning(f"Market ML Retraining notification error: {e}")
