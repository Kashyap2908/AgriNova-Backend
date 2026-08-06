import csv
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class FertilizerCatalog:
    """
    Service for dynamically retrieving fertilizer information from fertilizer_master.csv.
    """

    @staticmethod
    def get_all_fertilizers() -> list:
        """
        Reads D:/clg study/PROJECTS/p1/AgriNova-Backend/ml/data/fertilizer_master.csv
        and dynamically returns a list of dictionaries containing fertilizer data.
        """
        file_path = os.path.join(getattr(settings, 'BASE_DIR', ''), 'ml', 'data', 'fertilizer_master.csv')
        if not os.path.exists(file_path):
            file_path = r'D:\clg study\PROJECTS\p1\AgriNova-Backend\ml\data\fertilizer_master.csv'

        fertilizers = []
        if not os.path.exists(file_path):
            logger.error(f"Fertilizer master CSV file not found at path: {file_path}")
            return fertilizers

        try:
            with open(file_path, mode='r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    if not row or not row.get('Fertilizer_Name'):
                        continue

                    try:
                        n_pct = float(row.get('N_pct', 0) or 0)
                    except (ValueError, TypeError):
                        n_pct = 0.0

                    try:
                        p_pct = float(row.get('P_pct', 0) or 0)
                    except (ValueError, TypeError):
                        p_pct = 0.0

                    try:
                        k_pct = float(row.get('K_pct', 0) or 0)
                    except (ValueError, TypeError):
                        k_pct = 0.0

                    try:
                        price = float(row.get('Price_per_kg', 0) or 0)
                    except (ValueError, TypeError):
                        price = 0.0

                    fertilizers.append({
                        'name': row.get('Fertilizer_Name', '').strip(),
                        'type': row.get('Fertilizer_Type', '').strip(),
                        'n_pct': n_pct,
                        'p_pct': p_pct,
                        'k_pct': k_pct,
                        'price': price,
                        'method': row.get('Application_Method', '').strip(),
                        'form': row.get('Physical_Form', '').strip(),
                        'source': row.get('Source', '').strip(),
                    })
        except Exception as e:
            logger.error(f"Error reading fertilizer master CSV: {e}")

        return fertilizers
