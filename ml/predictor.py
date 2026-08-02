import numpy as np
import pandas as pd

CLS_FEATURE_COLS = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'Kharif', 'Rabi', 'Zaid']
REG_FEATURE_COLS = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'Kharif', 'Rabi', 'Zaid', 'crop_encoded', 'soil_encoded', 'water_encoded']

class Predictor:
    """
    Performs inference for Crop Recommendation (Classification) and Yield Prediction (Regression).
    Consumes pre-loaded models and encoders from ModelManager.
    """
    def __init__(self, crop_model, yield_model, label_encoder, feature_encoder):
        self.crop_model = crop_model
        self.yield_model = yield_model
        self.label_encoder = label_encoder
        self.feature_encoder = feature_encoder
        
        self.crop_classes = [c.strip().lower() for c in self.label_encoder.classes_]

    def _build_cls_dataframe(self, features: dict) -> pd.DataFrame:
        season = str(features.get('season', '')).strip().capitalize()
        kharif = 1 if season == 'Kharif' else 0
        rabi = 1 if season == 'Rabi' else 0
        zaid = 1 if season == 'Zaid' else 0

        row = [{
            'N': float(features.get('nitrogen', 0)),
            'P': float(features.get('phosphorus', 0)),
            'K': float(features.get('potassium', 0)),
            'temperature': float(features.get('temperature', 25)),
            'humidity': float(features.get('humidity', 60)),
            'ph': float(features.get('ph', 6.5)),
            'rainfall': float(features.get('rainfall', 100)),
            'Kharif': kharif,
            'Rabi': rabi,
            'Zaid': zaid
        }]
        return pd.DataFrame(row, columns=CLS_FEATURE_COLS)

    def _build_reg_dataframe(self, crop_name: str, features: dict) -> pd.DataFrame:
        df_cls = self._build_cls_dataframe(features)
        
        crop_clean = crop_name.strip().lower()
        if crop_clean in self.crop_classes:
            crop_encoded = int(self.label_encoder.transform([crop_clean])[0])
        else:
            crop_encoded = 0

        soil_map = self.feature_encoder.get('soil_encoder_map', {})
        soil_type = str(features.get('soil_type', 'Loam')).strip()
        soil_encoded = int(soil_map.get(soil_type, 0))

        water_map = self.feature_encoder.get('water_avail_map', {})
        water_avail = str(features.get('water_availability', 'medium')).strip().lower()
        water_encoded = int(water_map.get(water_avail, 2))

        df_reg = df_cls.copy()
        df_reg['crop_encoded'] = crop_encoded
        df_reg['soil_encoded'] = soil_encoded
        df_reg['water_encoded'] = water_encoded

        return df_reg[REG_FEATURE_COLS]

    def predict_crops(self, features: dict, valid_crops: list = None, top_k: int = 5) -> list:
        """
        Returns top recommended crops with confidence percentages.
        If valid_crops list is provided, restricts candidate selection to valid_crops matching State & Season.
        """
        X_df = self._build_cls_dataframe(features)
        probabilities = self.crop_model.predict_proba(X_df)[0]

        results = []
        valid_crops_clean = [c.strip().lower() for c in valid_crops] if valid_crops else None

        for idx, prob in enumerate(probabilities):
            crop_name = self.label_encoder.classes_[idx].title()
            crop_clean = crop_name.strip().lower()

            if valid_crops_clean is not None and crop_clean not in valid_crops_clean:
                continue

            results.append({
                "crop": crop_name,
                "confidence": round(float(prob) * 100, 2)
            })

        results.sort(key=lambda item: item['confidence'], reverse=True)

        if not results and valid_crops_clean:
            for idx, prob in enumerate(probabilities):
                results.append({
                    "crop": self.label_encoder.classes_[idx].title(),
                    "confidence": round(float(prob) * 100, 2)
                })
            results.sort(key=lambda item: item['confidence'], reverse=True)

        return results[:top_k]

    def predict_yield(self, crop_name: str, features: dict) -> float:
        """
        Predicts expected crop yield in kg/ha.
        """
        X_df = self._build_reg_dataframe(crop_name, features)
        predicted = self.yield_model.predict(X_df)[0]
        return round(float(predicted), 2)
