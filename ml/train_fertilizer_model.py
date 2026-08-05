import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from fertilizer_predictor import FertilizerPredictor

BASE_DIR = Path(__file__).parent.absolute()
MODELS_DIR = BASE_DIR / 'models'
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODELS_DIR / 'fertilizer_model.pkl'
ENCODERS_PATH = MODELS_DIR / 'fertilizer_encoders.pkl'

def generate_dataset(num_samples=3500):
    np.random.seed(42)
    predictor = FertilizerPredictor()

    crops = ['Rice', 'Maize', 'Chickpea', 'Kidneybeans', 'Pigeonpeas', 'Mothbeans', 
             'Mungbean', 'Blackgram', 'Lentil', 'Pomegranate', 'Banana', 'Mango', 
             'Grapes', 'Watermelon', 'Muskmelon', 'Apple', 'Orange', 'Papaya', 
             'Coconut', 'Cotton', 'Jute', 'Coffee', 'Wheat', 'Sugarcane']
    
    soil_types = ['Loamy', 'Clayey', 'Sandy', 'Black', 'Red', 'Alluvial', 'Silty']

    data = []
    for _ in range(num_samples):
        temp = np.random.uniform(15.0, 38.0)
        humidity = np.random.uniform(30.0, 90.0)
        moisture = np.random.uniform(20.0, 70.0)
        ph = np.random.uniform(5.2, 8.5)
        
        n = np.random.uniform(5.0, 140.0)
        p = np.random.uniform(5.0, 100.0)
        k = np.random.uniform(5.0, 120.0)
        
        soil = np.random.choice(soil_types)
        crop = np.random.choice(crops)

        req = predictor.get_crop_requirement(crop, "Basal / Sowing")
        ideal_n = float(req.get('Ideal_Nitrogen', 40.0))
        ideal_p = float(req.get('Ideal_Phosphorus', 40.0))
        ideal_k = float(req.get('Ideal_Potassium', 40.0))

        n_def = max(0.0, ideal_n - n)
        p_def = max(0.0, ideal_p - p)
        k_def = max(0.0, ideal_k - k)

        # Dynamic vector scoring assignment for ML dataset generation
        best_match = predictor.find_best_fertilizer_by_deficiency(n_def, p_def, k_def, ph)
        target = best_match.get('Fertilizer_Name', 'NPK 19-19-19')

        data.append({
            'temperature': temp,
            'humidity': humidity,
            'moisture': moisture,
            'ph': ph,
            'nitrogen': n,
            'phosphorus': p,
            'potassium': k,
            'soil_type': soil,
            'crop': crop,
            'fertilizer': target
        })

    return pd.DataFrame(data)

def train_and_save():
    df = generate_dataset()
    
    le_soil = LabelEncoder()
    le_crop = LabelEncoder()
    le_target = LabelEncoder()

    df['soil_enc'] = le_soil.fit_transform(df['soil_type'])
    df['crop_enc'] = le_crop.fit_transform(df['crop'])
    df['target_enc'] = le_target.fit_transform(df['fertilizer'])

    X = df[['temperature', 'humidity', 'moisture', 'ph', 'nitrogen', 'phosphorus', 'potassium', 'soil_enc', 'crop_enc']]
    y = df['target_enc']

    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(X, y)

    encoders = {
        'soil': le_soil,
        'crop': le_crop,
        'target': le_target
    }

    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODERS_PATH)

    print(f"[SUCCESS] Trained Dynamic Fertilizer ML Model saved to {MODEL_PATH}")
    print(f"[SUCCESS] Total unique predicted classes: {len(le_target.classes_)}")

if __name__ == '__main__':
    train_and_save()
