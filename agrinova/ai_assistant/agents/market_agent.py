from market_forecast.models import MarketForecastHistory

def get_market_context(farm_id):
    latest = MarketForecastHistory.objects.filter(farm_id=farm_id).first()
    if latest:
        return {
            "available": True,
            "crop": latest.crop,
            "best_market": latest.best_market,
            "best_modal_price": str(latest.best_modal_price),
            "forecast_price": str(latest.forecast_price) if latest.forecast_price else None,
            "trend": latest.trend,
            "recommendation": latest.recommendation
        }
    return {
        "available": False,
        "message": "No recent market forecast data is available for this farm."
    }
