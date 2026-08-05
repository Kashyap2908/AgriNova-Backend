import os
import pandas as pd
from ml.utils import get_dataset_path

_PROFIT_DF_CACHE = None

def get_profit_df():
    global _PROFIT_DF_CACHE
    if _PROFIT_DF_CACHE is None:
        csv_path = get_dataset_path('crop_state_season_mapping.csv')
        if os.path.exists(csv_path):
            try:
                _PROFIT_DF_CACHE = pd.read_csv(csv_path)
            except Exception:
                _PROFIT_DF_CACHE = pd.DataFrame()
        else:
            _PROFIT_DF_CACHE = pd.DataFrame()
    return _PROFIT_DF_CACHE

class CostLoaderService:
    """
    Loads agricultural cost dataset using Crop + State combination.
    Never modifies dataset files. Treats CSV as master dataset.
    Returns per-acre baseline costs (Seed, Fertilizer, Labour, Irrigation, Machinery, Other).
    """

    @staticmethod
    def get_crop_cost(crop_name: str, state_name: str) -> dict:
        df = get_profit_df()
        
        crop_clean = str(crop_name).strip().lower()
        state_clean = str(state_name).strip().lower()

        if not df.empty and 'Crop_Name' in df.columns and 'State' in df.columns:
            # 1. Exact crop + state match
            mask = (
                df['Crop_Name'].astype(str).str.strip().str.lower() == crop_clean
            ) & (
                df['State'].astype(str).str.strip().str.lower() == state_clean
            )
            matched = df[mask]

            # 2. Case-insensitive substring fallback if exact match empty
            if matched.empty:
                mask = (
                    df['Crop_Name'].astype(str).str.strip().str.lower().str.contains(crop_clean) |
                    df['Crop_Name'].astype(str).str.strip().str.lower().apply(lambda c: c in crop_clean)
                ) & (
                    df['State'].astype(str).str.strip().str.lower().str.contains(state_clean) |
                    df['State'].astype(str).str.strip().str.lower().apply(lambda s: s in state_clean)
                )
                matched = df[mask]

            # 3. Crop-only match fallback across any state
            if matched.empty:
                mask = df['Crop_Name'].astype(str).str.strip().str.lower() == crop_clean
                matched = df[mask]

            if not matched.empty:
                row = matched.iloc[0]
                seed = float(row.get('Seed_Cost', 1800))
                fertilizer = float(row.get('Fertilizer_Cost', 4000))
                labour = float(row.get('Labour_Cost', 8000))
                irrigation = float(row.get('Irrigation_Cost', 2500))
                machinery = float(row.get('Machinery_Cost', 3200))
                other = float(row.get('Other_Cost', 1500))
                total = float(row.get('Total_Cost', seed + fertilizer + labour + irrigation + machinery + other))
                source = str(row.get('Source', 'CACP Cost of Cultivation Scheme (DES, MoA&FW)'))
                last_updated = str(row.get('Last_Updated', '2024-2025'))

                return {
                    "seed_cost_per_acre": seed,
                    "fertilizer_cost_per_acre": fertilizer,
                    "labour_cost_per_acre": labour,
                    "irrigation_cost_per_acre": irrigation,
                    "machinery_cost_per_acre": machinery,
                    "other_cost_per_acre": other,
                    "total_cost_per_acre": total,
                    "source": source,
                    "last_updated": last_updated,
                    "is_fallback": False
                }

        # Fallback default government benchmark if dataset lookup completely misses
        return {
            "seed_cost_per_acre": 2000.0,
            "fertilizer_cost_per_acre": 4500.0,
            "labour_cost_per_acre": 8500.0,
            "irrigation_cost_per_acre": 2500.0,
            "machinery_cost_per_acre": 3500.0,
            "other_cost_per_acre": 1500.0,
            "total_cost_per_acre": 22500.0,
            "source": "Estimated using Government Average (CACP/DES Standards)",
            "last_updated": "2024-2025",
            "is_fallback": True
        }
