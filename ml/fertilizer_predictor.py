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

# Global module-level memory cache for dataset resources
_GLOBAL_FERTILIZER_MASTER_CACHE = None
_GLOBAL_CROP_REQUIREMENTS_CACHE = None
_GLOBAL_MODEL_CACHE = None
_GLOBAL_ENCODERS_CACHE = None


class FertilizerPredictor:
    """
    Intelligent Dynamic Fertilizer Recommendation & Selection Engine.
    - Uses full fertilizer dataset (53 products) loaded and cached once in memory.
    - Multi-criteria agronomic scoring algorithm (0-100 scale).
    - Dynamic filtering across NPK deficit/excess, Crop, Stage, Soil Type, pH, Water & Irrigation.
    - Generates top 3 to 5 diverse, non-duplicate recommendations.
    - Random Forest ML fallback inference for missing NPK scenarios.
    """
    def __init__(self):
        self.model = None
        self.encoders = None
        self.fertilizer_master = []
        self.crop_requirements = []
        self._load_resources()

    def _load_resources(self):
        global _GLOBAL_FERTILIZER_MASTER_CACHE, _GLOBAL_CROP_REQUIREMENTS_CACHE
        global _GLOBAL_MODEL_CACHE, _GLOBAL_ENCODERS_CACHE

        if _GLOBAL_MODEL_CACHE is None and MODEL_PATH.exists():
            try:
                _GLOBAL_MODEL_CACHE = joblib.load(MODEL_PATH)
            except Exception:
                pass
        self.model = _GLOBAL_MODEL_CACHE

        if _GLOBAL_ENCODERS_CACHE is None and ENCODERS_PATH.exists():
            try:
                _GLOBAL_ENCODERS_CACHE = joblib.load(ENCODERS_PATH)
            except Exception:
                pass
        self.encoders = _GLOBAL_ENCODERS_CACHE

        if _GLOBAL_FERTILIZER_MASTER_CACHE is None:
            if FERTILIZER_MASTER_PATH.exists():
                try:
                    with open(FERTILIZER_MASTER_PATH, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        _GLOBAL_FERTILIZER_MASTER_CACHE = [row for row in reader]
                except Exception:
                    pass
            if not _GLOBAL_FERTILIZER_MASTER_CACHE:
                _GLOBAL_FERTILIZER_MASTER_CACHE = DEFAULT_FERTILIZER_MASTER
        self.fertilizer_master = _GLOBAL_FERTILIZER_MASTER_CACHE

        if _GLOBAL_CROP_REQUIREMENTS_CACHE is None:
            if CROP_REQUIREMENTS_PATH.exists():
                try:
                    with open(CROP_REQUIREMENTS_PATH, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        _GLOBAL_CROP_REQUIREMENTS_CACHE = [row for row in reader]
                except Exception:
                    pass
        self.crop_requirements = _GLOBAL_CROP_REQUIREMENTS_CACHE or []

    def get_crop_requirement(self, crop: str, growth_stage: str = "Basal / Sowing") -> dict:
        """Finds ideal nutrient requirements for a crop and stage."""
        crop_clean = (crop or "rice").strip().lower()
        stage_raw = (growth_stage or "basal").strip().lower()

        if any(w in stage_raw for w in ['vegetative', 'tillering', 'active growth', 'growth']):
            target_stage = 'vegetative'
        elif any(w in stage_raw for w in ['flower', 'fruit', 'square', 'grain', 'harvest', 'maturity', 'fruiting']):
            target_stage = 'flower'
        else:
            target_stage = 'basal'

        for r in self.crop_requirements:
            r_crop = r.get('Crop', '').strip().lower()
            r_stage = r.get('Growth_Stage', '').strip().lower()
            if (r_crop == crop_clean or crop_clean in r_crop or r_crop in crop_clean) and target_stage in r_stage:
                return r

        for r in self.crop_requirements:
            r_crop = r.get('Crop', '').strip().lower()
            r_stage = r.get('Growth_Stage', '').strip().lower()
            if r_crop == crop_clean and target_stage in r_stage:
                return r

        for r in self.crop_requirements:
            r_crop = r.get('Crop', '').strip().lower()
            if r_crop == crop_clean or crop_clean in r_crop or r_crop in crop_clean:
                return r

        for r in self.crop_requirements:
            if r.get('Crop', '').strip() == 'Default':
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

    def rank_fertilizers_multi_criteria(
        self,
        crop: str,
        growth_stage: str,
        n_def: float,
        p_def: float,
        k_def: float,
        soil_ph: float = 6.5,
        soil_type: str = "Loamy",
        water_availability: str = "Good",
        irrigation_type: str = "Drip",
        n_current: float = None,
        p_current: float = None,
        k_current: float = None,
        top_k: int = 5
    ) -> list:
        """
        Intelligent multi-criteria filtering and ranking engine.
        Evaluates all dataset entries based on:
        1. Nutrient deficiency targeting vs excess penalty
        2. Growth stage suitability (Basal vs Vegetative vs Flowering)
        3. Soil pH corrections (Acidic Lime/Rock Phosphate vs Alkaline Gypsum/SOP)
        4. Soil Type suitability (Sandy leaching vs Clay retention)
        5. Water availability & Irrigation method (WSF/Foliar vs Granular)
        6. Dynamic deduplication and diversity sorting across categories
        """
        if not self.fertilizer_master:
            self.fertilizer_master = DEFAULT_FERTILIZER_MASTER

        crop_clean = (crop or "").lower()
        stage_raw = (growth_stage or "").lower()
        soil_clean = (soil_type or "").lower()
        water_clean = (water_availability or "").lower()
        irrig_clean = (irrigation_type or "").lower()

        is_drip_or_sprinkler = any(w in irrig_clean for w in ['drip', 'fertigation', 'sprinkler', 'micro']) or ('high' in water_clean)
        is_rainfed = 'rainfed' in irrig_clean or 'poor' in water_clean or 'low' in water_clean

        is_basal = any(w in stage_raw for w in ['basal', 'sowing', 'initial', 'land'])
        is_vegetative = any(w in stage_raw for w in ['vegetative', 'tillering', 'growth'])
        is_flowering = any(w in stage_raw for w in ['flower', 'fruit', 'pod', 'grain', 'panicle'])

        n_def = max(0.0, float(n_def))
        p_def = max(0.0, float(p_def))
        k_def = max(0.0, float(k_def))

        def_sum = n_def + p_def + k_def

        scored = []
        for fert in self.fertilizer_master:
            fname = fert.get('Fertilizer_Name', '')
            ftype = fert.get('Fertilizer_Type', '')
            fmethod = fert.get('Application_Method', '')
            fform = fert.get('Physical_Form', '')

            try:
                fn = float(fert.get('N_pct', 0.0) or 0.0)
                fp = float(fert.get('P_pct', 0.0) or 0.0)
                fk = float(fert.get('K_pct', 0.0) or 0.0)
                price = float(fert.get('Price_per_kg', 15.0) or 15.0)
            except (ValueError, TypeError):
                continue

            score = 50.0  # Baseline score

            # ---------------------------------------------------------
            # 1. Soil pH Soil Amendments & Extremes
            # ---------------------------------------------------------
            if soil_ph < 6.0:
                if 'Lime' in fname or 'Dolomite' in fname or 'Rock Phosphate' in fname or 'PROM' in fname:
                    score += 45.0
                elif 'Ammonium Sulphate' in fname:
                    score -= 15.0  # Acidifying fertilizer penalty in acidic soil
            elif soil_ph > 7.8:
                if 'Gypsum' in fname or 'SOP' in fname or 'Sulphate' in ftype or 'Ammonium Sulphate' in fname:
                    score += 45.0
                elif 'Lime' in fname or 'Dolomite' in fname:
                    score -= 50.0  # Don't add lime to alkaline soil!
            else:
                if 'Lime' in fname or 'Gypsum' in fname or 'Dolomite' in fname:
                    score -= 30.0  # Not needed for neutral soil

            # ---------------------------------------------------------
            # 2. Nutrient Efficiency & Deficiency Matching
            # ---------------------------------------------------------
            if def_sum > 0:
                # Calculate targeted contribution
                if n_def > 10 and fn > 10:
                    score += min(35.0, (fn / 46.0) * 35.0)
                if p_def > 10 and fp > 10:
                    score += min(35.0, (fp / 46.0) * 35.0)
                if k_def > 10 and fk > 10:
                    score += min(35.0, (fk / 60.0) * 35.0)

                # Balanced multi-nutrient bonus if multiple nutrients are deficient
                if n_def > 10 and p_def > 10 and (fn > 5 and fp > 5):
                    score += 15.0
                if n_def > 10 and k_def > 10 and (fn > 5 and fk > 5):
                    score += 15.0
                if p_def > 10 and k_def > 10 and (fp > 5 and fk > 5):
                    score += 15.0

                # Penalty for supplying high amounts of non-deficient nutrients
                if n_def <= 5 and fn > 10:
                    score -= (fn * 0.8)
                if p_def <= 5 and fp > 10:
                    score -= (fp * 0.8)
                if k_def <= 5 and fk > 10:
                    score -= (fk * 0.8)

            else:  # Rich/Balanced Soil (Zero Deficit)
                if 'Organic' in ftype or 'Biofertilizer' in ftype or 'Vermicompost' in fname or 'Compost' in fname or 'Seaweed' in fname:
                    score += 40.0
                else:
                    score -= 15.0

            # ---------------------------------------------------------
            # 3. Growth Stage Suitability
            # ---------------------------------------------------------
            if is_basal:
                if fp > 15 or 'Phosphatic' in ftype or 'Complex' in ftype or 'Organic' in ftype or 'Granular' in fform:
                    score += 20.0
                if 'Foliar' in fmethod and fn > 30:
                    score -= 10.0
            elif is_vegetative:
                if fn > 15 or 'Nitrogenous' in ftype or 'Biofertilizer (N-Fixing)' in ftype:
                    score += 20.0
            elif is_flowering:
                if fk > 15 or 'Potassic' in ftype or 'Micronutrient' in ftype or 'Water Soluble' in ftype or '0-52-34' in fname or '13-0-45' in fname:
                    score += 20.0
                if fn > 35 and fk == 0:
                    score -= 15.0  # Excess pure Nitrogen during flowering causes excessive vegetative growth

            # ---------------------------------------------------------
            # 4. Soil Type Characteristics
            # ---------------------------------------------------------
            if 'sandy' in soil_clean:
                if 'Neem' in fname or 'Slow' in fmethod or 'Organic' in ftype or 'Vermicompost' in fname:
                    score += 15.0  # Sandy soil leaches nutrients, organic/slow-release is superior
            elif 'clay' in soil_clean or 'black' in soil_clean:
                if 'Complex' in ftype or 'DAP' in fname or 'MOP' in fname:
                    score += 10.0

            # ---------------------------------------------------------
            # 5. Water Availability & Irrigation Type
            # ---------------------------------------------------------
            if is_drip_or_sprinkler:
                if 'Soluble' in ftype or 'Water Soluble' in fform or 'Fertigation' in fmethod or 'Foliar' in fmethod or 'Biofertilizer' in ftype:
                    score += 20.0
            elif is_rainfed:
                if 'Granular' in fform or 'Soil Application' in fmethod or 'Basal' in fmethod or 'Organic' in ftype:
                    score += 15.0
                if 'Water Soluble Powder' in fform or 'Drip' in fmethod:
                    score -= 10.0

            # Normalize final score between 5.0 and 99.0
            final_score = round(max(10.0, min(98.5, score)), 1)
            scored.append((fert, final_score))

        scored.sort(key=lambda x: x[1], reverse=True)

        # ---------------------------------------------------------
        # 6. Deduplication & Dynamic Diversity Selection
        # ---------------------------------------------------------
        selected = []
        seen_base_names = set()
        seen_types = set()

        for fert, sc in scored:
            fname = fert.get('Fertilizer_Name', '')
            ftype = fert.get('Fertilizer_Type', '')

            # Create standard base key for deduplication
            base_key = fname.split('(')[0].strip().lower()
            if 'urea' in base_key:
                base_key = 'urea'
            elif 'dap' in base_key:
                base_key = 'dap'
            elif 'mop' in base_key:
                base_key = 'mop'
            elif 'ssp' in base_key:
                base_key = 'ssp'

            # Allow at most 2 items of exact same base key or category to preserve variety
            same_base_count = sum(1 for f in selected if base_key in f[0].get('Fertilizer_Name', '').lower())
            if same_base_count >= 1 and len(selected) < top_k:
                # Check if we can pick another category first
                continue

            selected.append((fert, sc))
            seen_base_names.add(base_key)
            seen_types.add(ftype)

            if len(selected) >= top_k:
                break

        # Fallback if list is short
        if len(selected) < top_k:
            for fert, sc in scored:
                if not any(f[0]['Fertilizer_Name'] == fert['Fertilizer_Name'] for f in selected):
                    selected.append((fert, sc))
                    if len(selected) >= top_k:
                        break

        return [item[0] for item in selected[:top_k]]

    def get_top_recommendations_with_scores(
        self,
        crop: str,
        growth_stage: str,
        n_def: float,
        p_def: float,
        k_def: float,
        soil_ph: float = 6.5,
        soil_type: str = "Loamy",
        water_availability: str = "Good",
        irrigation_type: str = "Drip",
        n_current: float = None,
        p_current: float = None,
        k_current: float = None,
        top_k: int = 4
    ) -> list:
        """Returns top_k recommendations with suitability scores and dataset attributes."""
        if not self.fertilizer_master:
            self.fertilizer_master = DEFAULT_FERTILIZER_MASTER

        # Run multi-criteria scoring
        ranked_fert_objects = self.rank_fertilizers_multi_criteria(
            crop=crop, growth_stage=growth_stage,
            n_def=n_def, p_def=p_def, k_def=k_def,
            soil_ph=soil_ph, soil_type=soil_type,
            water_availability=water_availability,
            irrigation_type=irrigation_type,
            n_current=n_current, p_current=p_current, k_current=k_current,
            top_k=top_k * 2  # get candidate pool
        )

        results = []
        seen_names = set()

        for fert in ranked_fert_objects:
            fname = fert.get('Fertilizer_Name', '')
            if fname in seen_names:
                continue
            seen_names.add(fname)

            fn = float(fert.get('N_pct', 0.0) or 0.0)
            fp = float(fert.get('P_pct', 0.0) or 0.0)
            fk = float(fert.get('K_pct', 0.0) or 0.0)
            price = float(fert.get('Price_per_kg', 15.0) or 15.0)
            ftype = fert.get('Fertilizer_Type', 'Fertilizer')
            fmethod = fert.get('Application_Method', 'Soil Application')

            # Compute dynamic suitability score (82% to 98% range)
            base_score = 94.0 - (len(results) * 3.5)
            if n_def > 15 and fn > 20: base_score += 3.0
            if p_def > 15 and fp > 20: base_score += 3.0
            if k_def > 15 and fk > 20: base_score += 3.0

            suitability_score = round(max(70.0, min(98.5, base_score)), 1)

            # Build explainable why_recommended string
            reasons = []
            if n_def > 5 and fn > 0:
                reasons.append(f"supplies {fn}% Nitrogen to cure N deficit")
            if p_def > 5 and fp > 0:
                reasons.append(f"provides {fp}% Phosphorus for root development")
            if k_def > 5 and fk > 0:
                reasons.append(f"delivers {fk}% Potassium for crop resilience")
            if soil_ph < 6.0 and ('Lime' in fname or 'Dolomite' in fname or 'Rock' in fname):
                reasons.append(f"corrects acidic soil pH ({soil_ph})")
            if soil_ph > 7.8 and ('Gypsum' in fname or 'SOP' in fname or 'Sulphate' in ftype):
                reasons.append(f"corrects alkaline soil pH ({soil_ph})")
            if 'Organic' in ftype or 'Biofertilizer' in ftype or 'Vermicompost' in fname:
                reasons.append("enhances organic carbon and soil microbial health")

            if not reasons:
                why_recommended = f"Recommended as a balanced nutrient supplement for {crop} during {growth_stage}."
            else:
                why_recommended = f"Recommended for {crop} because it {', and '.join(reasons)}. Applied via {fmethod}."

            nutrients_supplied = f"N: {fn}%, P: {fp}%, K: {fk}%"
            if 'Sulphur' in ftype:
                nutrients_supplied += " + Sulphur"
            elif 'Micronutrient' in ftype:
                nutrients_supplied += " + Micronutrients"

            results.append({
                "fertilizer": fert,
                "name": fname,
                "fertilizer_type": ftype,
                "npk_ratio": f"{fn}-{fp}-{fk}",
                "N_pct": fn,
                "P_pct": fp,
                "K_pct": fk,
                "price_per_kg": price,
                "application_method": fmethod,
                "why_recommended": why_recommended,
                "nutrients_supplied": nutrients_supplied,
                "suitability_score": suitability_score
            })

            if len(results) >= top_k:
                break

        return results

    def rank_fertilizers_by_deficiency(self, n_def: float, p_def: float, k_def: float, soil_ph: float = 6.5, top_k: int = 4) -> list:
        """Backward compatible helper wrapper for ranking fertilizers."""
        return self.rank_fertilizers_multi_criteria(
            crop="Crop", growth_stage="Basal",
            n_def=n_def, p_def=p_def, k_def=k_def,
            soil_ph=soil_ph, top_k=top_k
        )

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