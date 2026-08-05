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

DEFAULT_FERTILIZER_MASTER = [
    {"Fertilizer_Name": "Urea", "Fertilizer_Type": "Nitrogenous", "N_pct": "46.0", "P_pct": "0.0", "K_pct": "0.0", "Price_per_kg": "5.5", "Application_Method": "Basal Soil Incorporation / Top Dressing", "Physical_Form": "Granular", "Source": "Govt Subsidy Standard"},
    {"Fertilizer_Name": "DAP (Di-Ammonium Phosphate)", "Fertilizer_Type": "Phosphatic & Nitrogenous", "N_pct": "18.0", "P_pct": "46.0", "K_pct": "0.0", "Price_per_kg": "27.0", "Application_Method": "Basal Application", "Physical_Form": "Granular", "Source": "IFFCO / KRIBHCO"},
    {"Fertilizer_Name": "MOP (Muriate of Potash)", "Fertilizer_Type": "Potassic", "N_pct": "0.0", "P_pct": "0.0", "K_pct": "60.0", "Price_per_kg": "34.0", "Application_Method": "Basal / Top Dressing", "Physical_Form": "Crystalline", "Source": "IPL Standard"},
    {"Fertilizer_Name": "NPK 19-19-19", "Fertilizer_Type": "Complex / Soluble", "N_pct": "19.0", "P_pct": "19.0", "K_pct": "19.0", "Price_per_kg": "140.0", "Application_Method": "Foliar Spray / Fertigation", "Physical_Form": "Water Soluble Powder", "Source": "General Commercial"},
    {"Fertilizer_Name": "NPK 12-32-16", "Fertilizer_Type": "Complex", "N_pct": "12.0", "P_pct": "32.0", "K_pct": "16.0", "Price_per_kg": "24.0", "Application_Method": "Basal Soil Incorporation", "Physical_Form": "Granular", "Source": "Gromor / IFFCO"},
    {"Fertilizer_Name": "NPK 10-26-26", "Fertilizer_Type": "Complex", "N_pct": "10.0", "P_pct": "26.0", "K_pct": "26.0", "Price_per_kg": "25.0", "Application_Method": "Basal Soil Incorporation", "Physical_Form": "Granular", "Source": "Gromor / Mahadhan"},
    {"Fertilizer_Name": "Single Super Phosphate (SSP)", "Fertilizer_Type": "Phosphatic", "N_pct": "0.0", "P_pct": "16.0", "K_pct": "0.0", "Price_per_kg": "9.0", "Application_Method": "Basal Soil Incorporation", "Physical_Form": "Granular", "Source": "General Commercial"},
    {"Fertilizer_Name": "Vermicompost (Organic)", "Fertilizer_Type": "Organic", "N_pct": "1.5", "P_pct": "1.0", "K_pct": "1.5", "Price_per_kg": "10.0", "Application_Method": "Soil Incorporation", "Physical_Form": "Organic Bulk", "Source": "Organic Standard"}
]

class FertilizerPredictor:
    """
    Predictor & Lookup Engine for Smart Fertilizer Recommendations.
    - Vector Cosine Similarity & Nutrient Utility Score Matching
    - Dynamic Lookup across fertilizer_master.csv
    - Random Forest ML Inference for Missing NPK scenarios
    """
    def __init__(self):
        self.model = None
        self.encoders = None
        self.fertilizer_master = []
        self.crop_requirements = []
        self._load_resources()

    def _load_resources(self):
        if self.model is None and MODEL_PATH.exists():
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception:
                pass
                
        if self.encoders is None and ENCODERS_PATH.exists():
            try:
                self.encoders = joblib.load(ENCODERS_PATH)
            except Exception:
                pass
            
        if FERTILIZER_MASTER_PATH.exists():
            try:
                with open(FERTILIZER_MASTER_PATH, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.fertilizer_master = [row for row in reader]
            except Exception:
                pass

        if not self.fertilizer_master:
            self.fertilizer_master = DEFAULT_FERTILIZER_MASTER

        if CROP_REQUIREMENTS_PATH.exists():
            try:
                with open(CROP_REQUIREMENTS_PATH, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.crop_requirements = [row for row in reader]
            except Exception:
                pass

    def get_crop_requirement(self, crop: str, growth_stage: str = "Basal / Sowing") -> dict:
        """Finds ideal nutrient requirements for a crop and stage."""
        crop_clean = crop.strip().lower()
        stage_raw = growth_stage.strip().lower()

        if any(w in stage_raw for w in ['vegetative', 'tillering', 'active growth', 'growth']):
            target_stage = 'vegetative'
        elif any(w in stage_raw for w in ['flower', 'fruit', 'square', 'grain', 'harvest', 'maturity', 'fruiting']):
            target_stage = 'flower'
        else:
            target_stage = 'basal'

        for r in self.crop_requirements:
            r_crop = r['Crop'].strip().lower()
            r_stage = r['Growth_Stage'].strip().lower()
            if (r_crop == crop_clean or crop_clean in r_crop or r_crop in crop_clean) and target_stage in r_stage:
                return r

        for r in self.crop_requirements:
            r_crop = r['Crop'].strip().lower()
            r_stage = r['Growth_Stage'].strip().lower()
            if r_crop == crop_clean and target_stage in r_stage:
                return r

        for r in self.crop_requirements:
            r_crop = r['Crop'].strip().lower()
            if r_crop == crop_clean or crop_clean in r_crop or r_crop in crop_clean:
                return r

        for r in self.crop_requirements:
            if r['Crop'].strip() == 'Default':
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

    def rank_fertilizers_by_deficiency(self, n_def: float, p_def: float, k_def: float, soil_ph: float = 6.5, top_k: int = 4) -> list:
        """
        Dynamically ranks all fertilizers in fertilizer_master.csv based on vector cosine similarity
        and nutrient deficit efficiency.
        """
        if not self.fertilizer_master:
            self.fertilizer_master = DEFAULT_FERTILIZER_MASTER

        # Handle pH extremes
        if soil_ph < 5.8:
            limes = [f for f in self.fertilizer_master if 'Lime' in f['Fertilizer_Name'] or 'Dolomite' in f['Fertilizer_Name']]
            if limes:
                return limes[:top_k]
        if soil_ph > 7.8:
            gypsums = [f for f in self.fertilizer_master if 'Gypsum' in f['Fertilizer_Name']]
            if gypsums:
                return gypsums[:top_k]

        n_def = max(0.0, float(n_def))
        p_def = max(0.0, float(p_def))
        k_def = max(0.0, float(k_def))

        def_sum = n_def + p_def + k_def

        # Zero deficit (Rich/Balanced Soil)
        if def_sum == 0:
            organics = [f for f in self.fertilizer_master if 'Organic' in f.get('Fertilizer_Type', '') or 'Vermicompost' in f['Fertilizer_Name'] or 'Compost' in f['Fertilizer_Name']]
            return organics[:top_k] if organics else self.fertilizer_master[:top_k]

        def_vec = np.array([n_def, p_def, k_def])
        def_norm = np.linalg.norm(def_vec)

        scored = []
        for fert in self.fertilizer_master:
            fname = fert.get('Fertilizer_Name', '')
            if 'Lime' in fname or 'Gypsum' in fname or 'Dolomite' in fname:
                continue

            try:
                fn = float(fert.get('N_pct', 0) or 0)
                fp = float(fert.get('P_pct', 0) or 0)
                fk = float(fert.get('K_pct', 0) or 0)
            except (ValueError, TypeError):
                continue

            fert_vec = np.array([fn, fp, fk])
            fert_norm = np.linalg.norm(fert_vec)

            if fert_norm == 0:
                continue

            cosine_sim = np.dot(def_vec, fert_vec) / (def_norm * fert_norm)

            # Penalty for supplying unwanted nutrient
            penalty = 0.0
            if n_def == 0 and fn > 2: penalty += fn * 1.2
            if p_def == 0 and fp > 2: penalty += fp * 1.2
            if k_def == 0 and fk > 2: penalty += fk * 1.2

            score = (cosine_sim * 100.0) + (min(fn + fp + fk, def_sum) * 0.3) - penalty
            scored.append((fert, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in scored[:top_k]]

    def find_best_fertilizer_by_deficiency(self, n_def: float, p_def: float, k_def: float, soil_ph: float = 6.5) -> dict:
        """Finds top single best fertilizer matching deficiency vector."""
        ranked = self.rank_fertilizers_by_deficiency(n_def, p_def, k_def, soil_ph, top_k=1)
        if ranked:
            return ranked[0]
        return self.fertilizer_master[0]

    def predict_ml_fertilizer(self, crop: str, soil_type: str, n: float, p: float, k: float, ph: float, temp: float = 28.0, humidity: float = 65.0, moisture: float = 45.0) -> str:
        """Uses trained Random Forest ML model to predict fertilizer."""
        if not self.model or not self.encoders:
            return "NPK 19-19-19"

        try:
            le_soil = self.encoders['soil']
            le_crop = self.encoders['crop']
            le_target = self.encoders['target']

            soil_enc = 0
            for idx, cls_name in enumerate(le_soil.classes_):
                if str(cls_name).lower() == str(soil_type).lower():
                    soil_enc = idx
                    break

            crop_enc = 0
            for idx, cls_name in enumerate(le_crop.classes_):
                if str(cls_name).lower() == str(crop).lower():
                    crop_enc = idx
                    break

            input_df = pd.DataFrame([{
                'temperature': float(temp),
                'humidity': float(humidity),
                'moisture': float(moisture),
                'ph': float(ph),
                'nitrogen': float(n),
                'phosphorus': float(p),
                'potassium': float(k),
                'soil_enc': soil_enc,
                'crop_enc': crop_enc
            }])
            pred_idx = self.model.predict(input_df)[0]
            predicted_name = le_target.inverse_transform([pred_idx])[0]
            return str(predicted_name)
        except Exception:
            return "NPK 19-19-19"

    def get_fertilizer_details(self, name: str) -> dict:
        """Retrieves row details from fertilizer_master.csv by name."""
        if not self.fertilizer_master:
            self.fertilizer_master = DEFAULT_FERTILIZER_MASTER

        name_clean = str(name).lower()
        for f in self.fertilizer_master:
            if name_clean in f['Fertilizer_Name'].lower():
                return f
        
        for f in self.fertilizer_master:
            if f['Fertilizer_Name'].lower() in name_clean:
                return f

        return self.fertilizer_master[0]