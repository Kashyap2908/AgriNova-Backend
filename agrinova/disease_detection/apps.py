import sys
from django.apps import AppConfig


class DiseaseDetectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'disease_detection'
    predictor = None

    def ready(self):
        # Only load the model once when the app is ready
        try:
            from ml.disease_predictor import DiseasePredictor
            self.predictor = DiseasePredictor()
            self.predictor._load_resources()
            print("[INFO] DiseasePredictor successfully loaded into memory.")
        except Exception as e:
            print(f"[ERROR] Failed to load DiseasePredictor: {e}")
