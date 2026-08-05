import os
import csv
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent / 'ml'
DATA_DIR = BASE_DIR / 'data'
FERTILIZER_MASTER_PATH = DATA_DIR / 'fertilizer_master.csv'

with open(FERTILIZER_MASTER_PATH, 'r', encoding='utf-8') as f:
    master = [row for row in csv.DictReader(f)]

def rank_fertilizers(n_def, p_def, k_def, soil_ph=6.5, top_k=3):
    if soil_ph < 5.8:
        return [f for f in master if 'Lime' in f['Fertilizer_Name'] or 'Dolomite' in f['Fertilizer_Name']][:top_k]
    if soil_ph > 7.8:
        return [f for f in master if 'Gypsum' in f['Fertilizer_Name']][:top_k]

    n_def, p_def, k_def = max(0.0, float(n_def)), max(0.0, float(p_def)), max(0.0, float(k_def))
    def_sum = n_def + p_def + k_def

    if def_sum == 0:
        return [f for f in master if 'Vermicompost' in f['Fertilizer_Name'] or 'City Compost' in f['Fertilizer_Name']][:top_k]

    def_vec = np.array([n_def, p_def, k_def])
    def_norm = np.linalg.norm(def_vec)

    scored = []
    for fert in master:
        fname = fert['Fertilizer_Name']
        if 'Lime' in fname or 'Gypsum' in fname or 'Dolomite' in fname:
            continue
        try:
            fn = float(fert.get('N_pct', 0) or 0)
            fp = float(fert.get('P_pct', 0) or 0)
            fk = float(fert.get('K_pct', 0) or 0)
        except ValueError:
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

        score = (cosine_sim * 100.0) + (min(fn+fp+fk, def_sum) * 0.3) - penalty
        scored.append((fert, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in scored[:top_k]]

test_cases = [
    ("High N Deficit, Low P&K", 50, 0, 0),
    ("High P Deficit, Low N&K", 0, 45, 0),
    ("High K Deficit, Low N&P", 0, 0, 50),
    ("High N & P Deficit, Low K", 40, 35, 0),
    ("High P & K Deficit, Low N", 0, 35, 35),
    ("Balanced High Deficit N, P, K", 35, 35, 35),
    ("Acidic Soil pH 5.2", 20, 20, 20, 5.2),
    ("Alkaline Soil pH 8.4", 20, 20, 20, 8.4),
    ("Zero Deficit (Rich Soil)", 0, 0, 0)
]

print("=== TESTING DYNAMIC NPK FERTILIZER VECTOR SELECTION ===")
for title, n, p, k, *ph in test_cases:
    soil_ph = ph[0] if ph else 6.5
    top = rank_fertilizers(n, p, k, soil_ph, top_k=3)
    best = top[0]['Fertilizer_Name']
    alts = [f['Fertilizer_Name'] for f in top[1:]]
    print(f"\nScenario: {title}")
    print(f"   Inputs -> N_def: {n}, P_def: {p}, K_def: {k}, pH: {soil_ph}")
    print(f"   -> Top Recommended: {best}")
    print(f"   -> Ranked Alternatives: {', '.join(alts)}")
