import csv
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_REQUIREMENTS = {'N': 120.0, 'P': 60.0, 'K': 40.0, 'pH': 6.5}


class CropRequirementEngine:
    """
    Engine for looking up ideal crop nutrient requirements (NPK & pH) based on crop and growth stage.
    """

    @staticmethod
    def get_ideal_requirements(crop: str, stage: str = 'Basal / Sowing') -> dict:
        """
        Reads crop_nutrient_requirements.csv and returns ideal N, P, K, pH requirement dictionary.
        Returns default values if the crop is not found.
        """
        if not crop:
            return DEFAULT_REQUIREMENTS.copy()

        crop_clean = crop.strip().lower()
        stage_clean = (stage or 'Basal / Sowing').strip().lower()

        file_path = os.path.join(getattr(settings, 'BASE_DIR', ''), 'ml', 'data', 'crop_nutrient_requirements.csv')
        if not os.path.exists(file_path):
            file_path = r'D:\clg study\PROJECTS\p1\AgriNova-Backend\ml\data\crop_nutrient_requirements.csv'

        if not os.path.exists(file_path):
            logger.error(f"Crop nutrient requirements CSV file not found at path: {file_path}")
            return DEFAULT_REQUIREMENTS.copy()

        exact_match = None
        crop_match_first_stage = None
        partial_match = None

        try:
            with open(file_path, mode='r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    if not row or not row.get('Crop'):
                        continue

                    row_crop = row.get('Crop', '').strip().lower()
                    row_stage = row.get('Growth_Stage', '').strip().lower()

                    if row_crop == crop_clean and row_stage == stage_clean:
                        exact_match = row
                        break
                    elif row_crop == crop_clean and crop_match_first_stage is None:
                        crop_match_first_stage = row
                    elif crop_clean in row_crop and partial_match is None:
                        partial_match = row

        except Exception as e:
            logger.error(f"Error reading crop nutrient requirements CSV: {e}")
            return DEFAULT_REQUIREMENTS.copy()

        matched_row = exact_match or crop_match_first_stage or partial_match
        if not matched_row:
            return DEFAULT_REQUIREMENTS.copy()

        try:
            n_val = float(matched_row.get('Ideal_Nitrogen', 120.0))
            p_val = float(matched_row.get('Ideal_Phosphorus', 60.0))
            k_val = float(matched_row.get('Ideal_Potassium', 40.0))
            ph_val = float(matched_row.get('Ideal_pH', 6.5))
            return {'N': n_val, 'P': p_val, 'K': k_val, 'pH': ph_val}
        except (ValueError, TypeError):
            return DEFAULT_REQUIREMENTS.copy()
