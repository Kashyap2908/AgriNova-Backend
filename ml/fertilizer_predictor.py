import os
import csv
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / 'data'
MODELS_DIR = BASE_DIR / 'models'

MODEL_PATH = MODELS_DIR / 'fertilizer_model.pkl'
ENCODERS_PATH = MODELS_DIR / 'fertilizer_encoders.pkl'
FERTILIZER_MASTER_PATH = DATA_DIR / 'fertilizer_master.csv'
CROP_REQUIREMENTS_PATH = DATA_DIR / 'crop_nutrient_requirements.csv'

class FertilizerPredictor:
    """
    Predictor & Lookup Engine for Smart Fertilizer Recommendations.
    - Loads trained ML Random Forest Model
    - Loads Fertilizer Master Lookup Dataset
    - Loads Crop Nutrient Requirement Dataset
    """
    def __init__(self):
        self.model = None
        self.encoders = None
        self.fertilizer_master = []
        self.crop_requirements = []
        self._load_resources()

    def _load_resources(self):
        if self.model is None and MODEL_PATH.exists():
            self.model = joblib.load(MODEL_PATH)
        if self.encoders is None and ENCODERS_PATH.exists():
            self.encoders = joblib.load(ENCODERS_PATH)
            
        if FERTILIZER_MASTER_PATH.exists():
            with open(FERTILIZER_MASTER_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.fertilizer_master = [row for row in reader]

        if CROP_REQUIREMENTS_PATH.exists():
            with open(CROP_REQUIREMENTS_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.crop_requirements = [row for row in reader]

    def get_crop_requirement(self, crop: str, growth_stage: str = "Basal / Sowing") -> dict:
        """Finds ideal nutrient requirements for a crop and stage."""
        crop_clean = crop.strip().title()
        
        # Exact crop + stage match
        for r in self.crop_requirements:
            if r['Crop'].lower() == crop_clean.lower() and growth_stage.lower() in r['Growth_Stage'].lower():
                return r
                
        # Crop match default stage
        for r in self.crop_requirements:
            if r['Crop'].lower() == crop_clean.lower():
                return r
                
        # Default fallback
        for r in self.crop_requirements:
            if r['Crop'] == 'Default':
                return r
                
        return {
            "Crop": crop,
            "Growth_Stage": growth_stage,
            "Ideal_Nitrogen": 40.0,
            "Ideal_Phosphorus": 40.0,
            "Ideal_Potassium": 40.0,
            "Ideal_pH": 6.5,
            "Source": "ICAR General Recommendation"
        }

    def find_best_fertilizer_by_deficiency(self, n_def: float, p_def: float, k_def: float, soil_ph: float = 6.5) -> dict:
        """
        Searches fertilizer_master.csv to find the fertilizer that best matches nutrient deficiencies.
        """
        if soil_ph < 5.8:
            for f in self.fertilizer_master:
                if 'Lime' in f['Fertilizer_Name']:
                    return f
        if soil_ph > 7.8:
            for f in self.fertilizer_master:
                if 'Gypsum' in f['Fertilizer_Name']:
                    return f

        # Determine highest deficit
        deficits = {'N': max(0.0, n_def), 'P': max(0.0, p_def), 'K': max(0.0, k_def)}
        primary_def = max(deficits, key=deficits.get)

        if deficits[primary_def] == 0:
            # Balanced nutrient state -> suggest organic or balanced NPK
            for f in self.fertilizer_master:
                if '19-19-19' in f['Fertilizer_Name']:
                    return f

        if primary_def == 'N' and deficits['P'] < 15:
            for f in self.fertilizer_master:
                if f['Fertilizer_Name'] == 'Urea':
                    return f

        if primary_def == 'P':
            for f in self.fertilizer_master:
                if 'DAP' in f['Fertilizer_Name']:
                    return f

        if primary_def == 'K':
            for f in self.fertilizer_master:
                if 'MOP' in f['Fertilizer_Name']:
                    return f

        # General score matching
        best_match = None
        best_score = -1.0
        for fert in self.fertilizer_master:
            try:
                fn = float(fert.get('N_pct', 0))
                fp = float(fert.get('P_pct', 0))
                fk = float(fert.get('K_pct', 0))
                score = (fn * n_def) + (fp * p_def) + (fk * k_def)
                if score > best_score:
                    best_score = score
                    best_match = fert
            except ValueError:
                continue

        return best_match or self.fertilizer_master[0]

    def predict_ml_fertilizer(self, crop: str, soil_type: str, n: float, p: float, k: float, ph: float, temp: float = 28.0, humidity: float = 65.0, moisture: float = 45.0) -> str:
        """Uses trained Random Forest ML model to predict fertilizer."""
        if not self.model or not self.encoders:
            return "Urea"

        try:
            le_soil = self.encoders['soil']
            le_crop = self.encoders['crop']
            le_target = self.encoders['target']

            # Safe label encoding with fallbacks
            soil_enc = le_soil.transform([soil_type])[0] if soil_type in le_soil.classes_ else 0
            crop_enc = le_crop.transform([crop])[0] if crop in le_crop.classes_ else 0

            input_features = np.array([[temp, humidity, moisture, ph, n, p, k, soil_enc, crop_enc]])
            pred_idx = self.model.predict(input_features)[0]
            return le_target.inverse_transform([pred_idx])[0]
        except Exception as e:
            return "Urea"

    def get_fertilizer_details(self, name: str) -> dict:
        """Retrieves row details from fertilizer_master.csv by name."""
        name_clean = name.lower()
        for f in self.fertilizer_master:
            if name_clean in f['Fertilizer_Name'].lower():
                return f
        return self.fertilizer_master[0] if self.fertilizer_master else {}