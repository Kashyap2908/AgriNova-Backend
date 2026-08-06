"""
Fertilizer Combination Optimizer Engine
Uses mathematical nutrient balancing and dataset-driven optimization (fertilizer_master.csv & crop_nutrient_requirements.csv)
to compute optimal multi-fertilizer blends for precision agriculture.
"""

import os
import csv
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

# Path resolutions
BASE_DIR = getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent.parent)
DATA_DIR = Path(BASE_DIR).parent / 'ml' / 'data'
if not DATA_DIR.exists():
    DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / 'ml' / 'data'

FERTILIZER_MASTER_PATH = DATA_DIR / 'fertilizer_master.csv'
CROP_REQUIREMENTS_PATH = DATA_DIR / 'crop_nutrient_requirements.csv'


class FertilizerOptimizer:
    """
    Mathematical & Rule-based Fertilizer Combination Optimizer.
    Derives NPK requirements from datasets and solves optimal blends using fertilizer_master.csv.
    """

    def __init__(self):
        self.fertilizer_catalog = self._load_fertilizer_catalog()
        self.crop_requirements = self._load_crop_requirements()

    def _load_fertilizer_catalog(self) -> list:
        catalog = []
        if not os.path.exists(FERTILIZER_MASTER_PATH):
            logger.error(f"Fertilizer master catalog not found at {FERTILIZER_MASTER_PATH}")
            return catalog

        try:
            with open(FERTILIZER_MASTER_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    catalog.append({
                        'name': row['Fertilizer_Name'].strip(),
                        'type': row['Fertilizer_Type'].strip(),
                        'N_pct': float(row.get('N_pct', 0.0) or 0.0),
                        'P_pct': float(row.get('P_pct', 0.0) or 0.0),
                        'K_pct': float(row.get('K_pct', 0.0) or 0.0),
                        'price_per_kg': float(row.get('Price_per_kg', 0.0) or 0.0),
                        'application_method': row.get('Application_Method', 'Soil Application').strip(),
                        'physical_form': row.get('Physical_Form', 'Granular').strip(),
                        'source': row.get('Source', 'Catalog').strip()
                    })
        except Exception as e:
            logger.error(f"Error reading fertilizer master CSV: {e}")
        return catalog

    def _load_crop_requirements(self) -> dict:
        requirements = {}
        if not os.path.exists(CROP_REQUIREMENTS_PATH):
            logger.error(f"Crop requirements CSV not found at {CROP_REQUIREMENTS_PATH}")
            return requirements

        try:
            with open(CROP_REQUIREMENTS_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    crop_name = row['Crop'].strip().lower()
                    if crop_name not in requirements:
                        requirements[crop_name] = []
                    
                    requirements[crop_name].append({
                        'stage': row.get('Growth_Stage', '').strip(),
                        'N': float(row.get('Ideal_Nitrogen', 0.0) or 0.0),
                        'P': float(row.get('Ideal_Phosphorus', 0.0) or 0.0),
                        'K': float(row.get('Ideal_Potassium', 0.0) or 0.0),
                        'pH': float(row.get('Ideal_pH', 6.5) or 6.5)
                    })
        except Exception as e:
            logger.error(f"Error reading crop requirements CSV: {e}")
        return requirements

    def get_crop_ideal_requirement(self, crop: str) -> dict:
        """
        Calculates total crop nutrient requirement (kg/ha) across stages from crop_nutrient_requirements.csv.
        """
        crop_clean = (crop or '').strip().lower()
        
        # Priority 1: Exact match in dataset
        matched_stages = self.crop_requirements.get(crop_clean)

        # Priority 2: Word boundary match (e.g. 'wheat' matching 'wheat grain', but NOT 'buckwheat')
        if not matched_stages:
            import re
            pattern = r'\b' + re.escape(crop_clean) + r'\b'
            for c_key, stages in self.crop_requirements.items():
                if re.search(pattern, c_key):
                    matched_stages = stages
                    break

        # Priority 3: Substring fallback
        if not matched_stages:
            for c_key, stages in self.crop_requirements.items():
                if c_key in crop_clean or crop_clean in c_key:
                    matched_stages = stages
                    break

        if not matched_stages:
            # Agronomic default fallback for unlisted crops
            return {'N': 120.0, 'P': 60.0, 'K': 40.0, 'pH': 6.8, 'stages': []}

        total_n = sum(s['N'] for s in matched_stages)
        total_p = sum(s['P'] for s in matched_stages)
        total_k = sum(s['K'] for s in matched_stages)
        avg_ph = matched_stages[0]['pH'] if matched_stages else 6.5

        return {
            'N': round(total_n, 1),
            'P': round(total_p, 1),
            'K': round(total_k, 1),
            'pH': avg_ph,
            'stages': matched_stages
        }

    def _find_item(self, keywords: list, default_item: dict) -> dict:
        """Helper to find fertilizer by keywords from master catalog."""
        for kw in keywords:
            matched = next((f for f in self.fertilizer_catalog if kw.lower() in f['name'].lower()), None)
            if matched:
                return matched
        return default_item

    def solve_fertilizer_combinations(self, target_n: float, target_p: float, target_k: float,
                                       crop: str = '', soil_ph: float = 7.0, soil_type: str = '') -> list:
        """
        Dynamically solves candidate multi-fertilizer combinations using fertilizer_master.csv.
        Ranks options dynamically based on crop suitability, soil pH, sulphur need, and master catalog prices.
        """
        target_n = max(0.0, target_n)
        target_p = max(0.0, target_p)
        target_k = max(0.0, target_k)
        crop_clean = (crop or '').strip().lower()

        # Catalog Item Lookups
        urea = self._find_item(['Neem Coated Urea', 'Urea'], {'name': 'Neem Coated Urea', 'N_pct': 46.0, 'P_pct': 0.0, 'K_pct': 0.0, 'price_per_kg': 6.0})
        dap = self._find_item(['DAP (Di-Ammonium Phosphate)', 'DAP'], {'name': 'DAP (Di-Ammonium Phosphate)', 'N_pct': 18.0, 'P_pct': 46.0, 'K_pct': 0.0, 'price_per_kg': 27.0})
        mop = self._find_item(['MOP (Muriate of Potash)', 'MOP'], {'name': 'MOP (Muriate of Potash)', 'N_pct': 0.0, 'P_pct': 0.0, 'K_pct': 60.0, 'price_per_kg': 34.0})
        sop = self._find_item(['Sulphate of Potash (SOP 0-0-50)', 'Sulphate of Potash'], {'name': 'SOP (Sulphate of Potash)', 'N_pct': 0.0, 'P_pct': 0.0, 'K_pct': 50.0, 'price_per_kg': 85.0})
        ssp = self._find_item(['Single Super Phosphate (SSP)', 'SSP'], {'name': 'Single Super Phosphate (SSP)', 'N_pct': 0.0, 'P_pct': 16.0, 'K_pct': 0.0, 'price_per_kg': 9.0})
        npk_12_32_16 = self._find_item(['NPK 12-32-16'], {'name': 'NPK 12-32-16', 'N_pct': 12.0, 'P_pct': 32.0, 'K_pct': 16.0, 'price_per_kg': 24.0})
        npk_10_26_26 = self._find_item(['NPK 10-26-26'], {'name': 'NPK 10-26-26', 'N_pct': 10.0, 'P_pct': 26.0, 'K_pct': 26.0, 'price_per_kg': 25.0})
        npk_14_35_14 = self._find_item(['NPK 14-35-14'], {'name': 'NPK 14-35-14', 'N_pct': 14.0, 'P_pct': 35.0, 'K_pct': 14.0, 'price_per_kg': 26.0})
        npk_20_20_0 = self._find_item(['NPK 20-20-0-13', 'NPK 16-20-0-13'], {'name': 'NPK 20-20-0-13', 'N_pct': 20.0, 'P_pct': 20.0, 'K_pct': 0.0, 'price_per_kg': 21.0})
        amm_sulphate = self._find_item(['Ammonium Sulphate'], {'name': 'Ammonium Sulphate', 'N_pct': 20.6, 'P_pct': 0.0, 'K_pct': 0.0, 'price_per_kg': 14.0})
        prom = self._find_item(['PROM (Phosphate Rich Organic Manure)', 'PROM'], {'name': 'PROM (Phosphate Rich Organic Manure)', 'N_pct': 0.4, 'P_pct': 10.4, 'K_pct': 0.4, 'price_per_kg': 14.0})

        candidates = []

        # STRATEGY 1: Classical High-Efficiency Straight (DAP + Urea + MOP)
        dap_kg = (target_p / (dap['P_pct'] / 100.0)) if dap['P_pct'] > 0 else 0.0
        n_from_dap = dap_kg * (dap['N_pct'] / 100.0)
        urea_kg1 = max(0.0, target_n - n_from_dap) / (urea['N_pct'] / 100.0) if urea['N_pct'] > 0 else 0.0
        mop_kg1 = (target_k / (mop['K_pct'] / 100.0)) if mop['K_pct'] > 0 else 0.0
        
        items1 = []
        names1 = []
        if dap_kg >= 1.0: 
            items1.append({'fertilizer': dap, 'dose_kg_ha': round(dap_kg, 1)})
            names1.append('DAP')
        if urea_kg1 >= 1.0: 
            items1.append({'fertilizer': urea, 'dose_kg_ha': round(urea_kg1, 1)})
            names1.append('Urea')
        if mop_kg1 >= 1.0: 
            items1.append({'fertilizer': mop, 'dose_kg_ha': round(mop_kg1, 1)})
            names1.append('MOP')
        
        if items1:
            title1 = f"High-Efficiency Straight Combination ({' + '.join(names1)})" if len(names1) > 1 else f"Straight Application ({names1[0]})"
            candidates.append({
                'title': title1,
                'description': 'Standard high-concentration straight fertilizer combination tailored to your soil.',
                'items': items1,
                'tag': 'MOST ECONOMICAL',
                'strategy': 'STRAIGHT_DAP'
            })

        # STRATEGY 2: Complex High-Phosphorus Granular Blend (NPK 12-32-16 + Urea + MOP)
        comp_kg2 = (target_p / (npk_12_32_16['P_pct'] / 100.0)) if npk_12_32_16['P_pct'] > 0 else 0.0
        n_from_comp2 = comp_kg2 * (npk_12_32_16['N_pct'] / 100.0)
        k_from_comp2 = comp_kg2 * (npk_12_32_16['K_pct'] / 100.0)
        urea_kg2 = max(0.0, target_n - n_from_comp2) / (urea['N_pct'] / 100.0) if urea['N_pct'] > 0 else 0.0
        mop_kg2 = max(0.0, target_k - k_from_comp2) / (mop['K_pct'] / 100.0) if mop['K_pct'] > 0 else 0.0

        items2 = []
        names2 = []
        if comp_kg2 >= 1.0: 
            items2.append({'fertilizer': npk_12_32_16, 'dose_kg_ha': round(comp_kg2, 1)})
            names2.append('NPK 12-32-16')
        if urea_kg2 >= 1.0: 
            items2.append({'fertilizer': urea, 'dose_kg_ha': round(urea_kg2, 1)})
            names2.append('Urea')
        if mop_kg2 >= 1.0: 
            items2.append({'fertilizer': mop, 'dose_kg_ha': round(mop_kg2, 1)})
            names2.append('MOP')

        if items2 and comp_kg2 >= 1.0:
            title2 = f"Complex Balanced Blend ({' + '.join(names2)})" if len(names2) > 1 else f"Balanced Application ({names2[0]})"
            candidates.append({
                'title': title2,
                'description': 'Uniform multi-nutrient complex granules for balanced root and tillering growth.',
                'items': items2,
                'tag': 'BALANCED GRANULES',
                'strategy': 'COMPLEX_12_32_16'
            })

        # STRATEGY 3: Sulphur & Calcium Enriched Pulse/Oilseed Formulation (SSP + Urea / Ammonium Sulphate + MOP)
        ssp_kg3 = (target_p / (ssp['P_pct'] / 100.0)) if ssp['P_pct'] > 0 else 0.0
        # For oilseeds/pulses, use Ammonium Sulphate to supply extra Sulphur if available
        n_fert3 = amm_sulphate if any(k in crop_clean for k in ['mustard', 'groundnut', 'soybean']) else urea
        urea_kg3 = (target_n / (n_fert3['N_pct'] / 100.0)) if n_fert3['N_pct'] > 0 else 0.0
        mop_kg3 = (target_k / (mop['K_pct'] / 100.0)) if mop['K_pct'] > 0 else 0.0

        items3 = []
        names3 = []
        if ssp_kg3 >= 1.0: 
            items3.append({'fertilizer': ssp, 'dose_kg_ha': round(ssp_kg3, 1)})
            names3.append('SSP')
        if urea_kg3 >= 1.0: 
            items3.append({'fertilizer': n_fert3, 'dose_kg_ha': round(urea_kg3, 1)})
            names3.append(n_fert3['name'])
        if mop_kg3 >= 1.0: 
            items3.append({'fertilizer': mop, 'dose_kg_ha': round(mop_kg3, 1)})
            names3.append('MOP')

        if items3 and ssp_kg3 >= 1.0:
            title3 = f"Sulphur & Calcium Enriched Formulation ({' + '.join(names3)})" if len(names3) > 1 else f"Enriched Application ({names3[0]})"
            candidates.append({
                'title': title3,
                'description': 'Supplies Water Soluble P2O5, Sulphur & Calcium; ideal for pulses, oilseeds & acidic soils.',
                'items': items3,
                'tag': 'HIGH SULPHUR & CALCIUM',
                'strategy': 'SULPHUR_SSP'
            })

        # STRATEGY 4: Potassic Tuber & Vegetable Specialist (NPK 10-26-26 + SOP / MOP + Urea)
        comp_kg4 = (target_k / (npk_10_26_26['K_pct'] / 100.0)) if npk_10_26_26['K_pct'] > 0 else 0.0
        n_from_comp4 = comp_kg4 * (npk_10_26_26['N_pct'] / 100.0)
        p_from_comp4 = comp_kg4 * (npk_10_26_26['P_pct'] / 100.0)
        
        rem_p4 = max(0.0, target_p - p_from_comp4)
        dap_kg4 = (rem_p4 / (dap['P_pct'] / 100.0)) if dap['P_pct'] > 0 else 0.0
        n_from_dap4 = dap_kg4 * (dap['N_pct'] / 100.0)
        
        urea_kg4 = max(0.0, target_n - n_from_comp4 - n_from_dap4) / (urea['N_pct'] / 100.0) if urea['N_pct'] > 0 else 0.0
        
        items4 = []
        names4 = []
        if comp_kg4 >= 1.0: 
            items4.append({'fertilizer': npk_10_26_26, 'dose_kg_ha': round(comp_kg4, 1)})
            names4.append('NPK 10-26-26')
        if dap_kg4 >= 1.0: 
            items4.append({'fertilizer': dap, 'dose_kg_ha': round(dap_kg4, 1)})
            names4.append('DAP')
        if urea_kg4 >= 1.0: 
            items4.append({'fertilizer': urea, 'dose_kg_ha': round(urea_kg4, 1)})
            names4.append('Urea')

        if items4 and comp_kg4 >= 1.0:
            title4 = f"High Potash Vegetable & Tuber Blend ({' + '.join(names4)})" if len(names4) > 1 else f"High Potash Application ({names4[0]})"
            candidates.append({
                'title': title4,
                'description': 'High Potassium ratio for maximum tuber starch development and fruit skin shine.',
                'items': items4,
                'tag': 'HIGH POTASH & TUBER SPECIALIST',
                'strategy': 'POTASH_10_26_26'
            })

        # STRATEGY 5: Organic-Rich Phosphate Formulation (PROM + Urea + MOP)
        prom_kg5 = (target_p / (prom['P_pct'] / 100.0)) if prom['P_pct'] > 0 else 0.0
        urea_kg5 = (target_n / (urea['N_pct'] / 100.0)) if urea['N_pct'] > 0 else 0.0
        mop_kg5 = (target_k / (mop['K_pct'] / 100.0)) if mop['K_pct'] > 0 else 0.0

        items5 = []
        names5 = []
        if prom_kg5 >= 1.0: 
            items5.append({'fertilizer': prom, 'dose_kg_ha': round(prom_kg5, 1)})
            names5.append('PROM')
        if urea_kg5 >= 1.0: 
            items5.append({'fertilizer': urea, 'dose_kg_ha': round(urea_kg5, 1)})
            names5.append('Urea')
        if mop_kg5 >= 1.0: 
            items5.append({'fertilizer': mop, 'dose_kg_ha': round(mop_kg5, 1)})
            names5.append('MOP')

        if items5 and prom_kg5 >= 1.0:
            title5 = f"Organic Eco-Enriched Formulation ({' + '.join(names5)})" if len(names5) > 1 else f"Organic Eco-Enriched ({names5[0]})"
            candidates.append({
                'title': title5,
                'description': 'Phosphate Rich Organic Manure improves soil organic carbon and micro-flora activity.',
                'items': items5,
                'tag': 'ECO ORGANIC ENRICHED',
                'strategy': 'ORGANIC_PROM'
            })

        # Calculate dynamic weighted score for each candidate option using crop, soil_ph, and master catalog prices
        for cand in candidates:
            cand['score'] = self._calculate_dynamic_score(
                cand['items'], target_n, target_p, target_k, crop_clean, soil_ph, soil_type, cand['strategy']
            )

        # Sort candidates by dynamic suitability score (highest first)
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:3]

    def _calculate_dynamic_score(self, items: list, target_n: float, target_p: float, target_k: float,
                                 crop: str, soil_ph: float, soil_type: str, strategy: str) -> float:
        """
        Calculates dynamic suitability score (0-100%):
        - Nutrient Match Precision (35%)
        - Crop Agronomic Specificity (30%)
        - Price Efficiency from master catalog (15%)
        - Soil pH Compatibility (10%)
        - Application Ease & Availability (10%)
        """
        if not items:
            return 50.0

        # 1. Nutrient Supply Precision
        total_n = sum(item['dose_kg_ha'] * (item['fertilizer']['N_pct'] / 100.0) for item in items)
        total_p = sum(item['dose_kg_ha'] * (item['fertilizer']['P_pct'] / 100.0) for item in items)
        total_k = sum(item['dose_kg_ha'] * (item['fertilizer']['K_pct'] / 100.0) for item in items)

        n_match = 1.0 - (abs(total_n - target_n) / (target_n + 1.0))
        p_match = 1.0 - (abs(total_p - target_p) / (target_p + 1.0))
        k_match = 1.0 - (abs(total_k - target_k) / (target_k + 1.0))
        nutrient_score = max(0.0, min(1.0, (n_match + p_match + k_match) / 3.0)) * 35.0

        # 2. Crop Agronomic Specificity (30%)
        crop_score = 20.0
        
        # Pulses & Legumes (Chickpea, Soybean, Groundnut) -> SSP & Organic PROM thrive!
        if any(leg in crop for leg in ['chickpea', 'soybean', 'groundnut', 'gram', 'moong', 'urad', 'arhar', 'tur']):
            if strategy in ['SULPHUR_SSP', 'ORGANIC_PROM']:
                crop_score += 10.0
            elif strategy == 'COMPLEX_12_32_16':
                crop_score += 6.0
        
        # Oilseeds (Mustard, Groundnut, Soybean) -> Sulphur enriched SSP/Ammonium Sulphate thrives!
        elif any(oil in crop for oil in ['mustard', 'soybean', 'groundnut', 'sunflower', 'sesame']):
            if strategy == 'SULPHUR_SSP':
                crop_score += 10.0
            elif strategy == 'COMPLEX_12_32_16':
                crop_score += 7.0

        # Vegetables & Tubers (Potato, Tomato, Onion, Chilli) -> High Potash 10-26-26 thrives!
        elif any(veg in crop for veg in ['potato', 'tomato', 'onion', 'chilli', 'brinjal', 'vegetable']):
            if strategy == 'POTASH_10_26_26':
                crop_score += 10.0
            elif strategy == 'COMPLEX_12_32_16':
                crop_score += 7.0

        # Cereals & Heavy Feeders (Wheat, Rice, Paddy, Maize, Sugarcane, Cotton)
        elif any(cer in crop for cer in ['wheat', 'rice', 'paddy', 'maize', 'sugarcane', 'cotton']):
            if strategy in ['STRAIGHT_DAP', 'COMPLEX_12_32_16']:
                crop_score += 10.0

        # 3. Price Efficiency (15%) - calculated directly from master catalog price!
        total_cost_ha = sum(item['dose_kg_ha'] * item['fertilizer']['price_per_kg'] for item in items)
        # Lower cost per ha gets higher score (scaled relative to 4000 INR baseline)
        price_ratio = max(0.5, min(1.5, total_cost_ha / 3500.0))
        price_score = max(5.0, min(15.0, 15.0 - (price_ratio - 1.0) * 5.0))

        # 4. Soil pH Compatibility (10%)
        ph_score = 8.0
        if soil_ph < 6.2 and strategy in ['SULPHUR_SSP', 'ORGANIC_PROM']:
            ph_score += 2.0  # SSP & PROM do not fix in acidic soils like DAP
        elif soil_ph > 7.8 and strategy == 'SULPHUR_SSP':
            ph_score += 2.0  # Sulphur lowers rhizosphere pH in alkaline soils

        # 5. Application Ease & Availability (10%)
        avail_score = 9.0 if strategy in ['STRAIGHT_DAP', 'COMPLEX_12_32_16'] else 8.0

        final_score = round(nutrient_score + crop_score + price_score + ph_score + avail_score, 1)
        return min(98.0, max(72.0, final_score))
