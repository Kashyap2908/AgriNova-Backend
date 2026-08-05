from recommendation.models import RecommendationHistory

def get_crop_context(farm_id):
    latest = RecommendationHistory.objects.filter(farm_id=farm_id).first()
    if latest:
        return {
            "available": True,
            "recommended_crop": latest.recommended_crop,
            "expected_yield": latest.expected_yield,
            "explanation": latest.explanation,
            "soil_inputs": latest.input_values,
            "confidence": latest.confidence
        }
    return {
        "available": False,
        "message": "No crop recommendation history exists for this farm."
    }
