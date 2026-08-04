from django.test import TestCase
from django.utils import timezone
from .models import MarketCache
from .services.market_cache_service import MarketCacheService
from ml.market_model_manager import MarketModelManager

class MarketCacheAndMLTestCase(TestCase):
    def setUp(self):
        self.crop = "Cotton"
        self.state = "Gujarat"
        self.district = "Rajkot"
        self.market = "Rajkot APMC"

    def test_market_cache_creation_and_uniqueness(self):
        cache = MarketCache.objects.create(
            crop=self.crop,
            state=self.state,
            district=self.district,
            market=self.market,
            current_price={
                "crop": self.crop,
                "state": self.state,
                "district": self.district,
                "market": self.market,
                "minimum_price": 7200.0,
                "modal_price": 7500.0,
                "maximum_price": 7800.0,
                "last_updated": timezone.now().strftime("%Y-%m-%d")
            }
        )
        self.assertIsNotNone(cache.id)
        self.assertEqual(cache.crop, "Cotton")

    def test_history_rotation_limits(self):
        cache = MarketCache.objects.create(
            crop=self.crop,
            state=self.state,
            district=self.district,
            market=self.market
        )

        # Simulate 10 days of entries to test rolling rotation limits
        for i in range(10):
            date_str = f"2026-08-{i+1:02d}"
            MarketCacheService._append_today_price_and_rotate(
                cache, date_str, 7000.0 + i * 10, 7200.0 + i * 10, 7500.0 + i * 10
            )

        # Weekly history must strictly cap at 7 items
        self.assertEqual(len(cache.weekly_price_history), 7)
        # Monthly history should have 10 items (< 30)
        self.assertEqual(len(cache.monthly_price_history), 10)
        # Yearly history should have 10 items (< 365)
        self.assertEqual(len(cache.yearly_price_history), 10)

    def test_ml_prediction_inference(self):
        predictor = MarketModelManager.get_instance().get_predictor()
        current_price_info = {
            "crop": "Cotton",
            "modal_price": 7500.0,
            "minimum_price": 7200.0,
            "maximum_price": 7800.0,
            "last_updated": timezone.now().strftime("%Y-%m-%d")
        }
        historical_records = [
            {"date": f"2026-07-{i:02d}", "modal_price": 7400.0 + i * 5} for i in range(1, 31)
        ]

        predictions = predictor.predict_market_intelligence(current_price_info, historical_records)

        self.assertIn("short_term_10_days", predictions)
        self.assertIn("medium_term_months", predictions)

        # Check Short-Term 10 Days
        short_term = predictions["short_term_10_days"]
        self.assertEqual(len(short_term), 10)
        self.assertIn("predicted_modal_price", short_term[0])

        # Check Medium-Term 4 Months
        medium_term = predictions["medium_term_months"]
        self.assertEqual(len(medium_term), 4)
        self.assertIn("predicted_avg_price", medium_term[0])
        self.assertIn("trend", medium_term[0])
