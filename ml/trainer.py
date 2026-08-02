import os
import time
import datetime
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, r2_score, mean_absolute_error
from xgboost import XGBClassifier, XGBRegressor

from ml.utils import (
    get_dataset_path,
    get_model_path,
    compute_file_hash,
    get_file_mtime,
    save_json
)

SOIL_TYPES_DEFAULT = [
    'Clay loam', 'Clayey', 'Alluvial', 'Red loam', 'Sandy loam',
    'Black cotton', 'Loam', 'Sandy', 'Peaty', 'Laterite', 'Silt loam',
    'Coastal sand', 'Gravelly', 'Acidic loam', 'Vertisol', 'Poor sandy',
    'Heavy clay', 'Arid soil', 'Saline', 'Wasteland', 'Deep loam'
]

WATER_AVAIL_MAP = {
    'low': 1,
    'medium': 2,
    'high': 3
}

def train_all_models() -> dict:
    """
    Trains XGBoost Crop Classifier and Yield Regressor models on Crop_recommendation_extended.csv.
    Saves trained models, encoders, and model_metadata.json into ml/models/.
    """
    print("[ML Trainer] Starting model training workflow with XGBoost...")
    dataset_path = get_dataset_path('Crop_recommendation_extended.csv')
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found at {dataset_path}")

    # Load dataset
    df = pd.read_csv(dataset_path)
    
    # Drop rows missing essential features
    essential_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label', 'Expected_Yield']
    df = df.dropna(subset=essential_cols).copy()

    # Ensure season columns exist or derive them
    if 'Kharif' not in df.columns:
        df['Kharif'] = 0
    if 'Rabi' not in df.columns:
        df['Rabi'] = 0
    if 'Zaid' not in df.columns:
        df['Zaid'] = 0

    # Ensure Soil_Type and Water_Availability exist
    if 'Soil_Type' not in df.columns:
        df['Soil_Type'] = 'Loam'
    if 'Water_Availability' not in df.columns:
        df['Water_Availability'] = 'Medium'

    # --- 1. Fit LabelEncoder for Crops ---
    label_encoder = LabelEncoder()
    df['crop_encoded'] = label_encoder.fit_transform(df['label'].str.strip().str.lower())
    
    # Save label encoder
    joblib.dump(label_encoder, get_model_path('label_encoder.pkl'))

    # --- 2. Build Feature Encoders for Soil & Water ---
    soil_types = sorted(list(set(df['Soil_Type'].dropna().astype(str).str.strip().tolist())))
    soil_encoder_map = {soil: idx for idx, soil in enumerate(soil_types)}

    feature_encoder = {
        'soil_encoder_map': soil_encoder_map,
        'water_avail_map': WATER_AVAIL_MAP
    }
    joblib.dump(feature_encoder, get_model_path('feature_encoder.pkl'))

    # --- 3. Train Crop Classification Model (XGBClassifier) ---
    cls_feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'Kharif', 'Rabi', 'Zaid']
    X_cls = df[cls_feature_cols]
    y_cls = df['crop_encoded']

    X_cls_train, X_cls_test, y_cls_train, y_cls_test = train_test_split(
        X_cls, y_cls, test_size=0.15, random_state=42, stratify=y_cls
    )

    crop_model = XGBClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="multi:softprob",
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1
    )
    
    cls_start_time = time.time()
    crop_model.fit(X_cls_train, y_cls_train)
    cls_train_time = time.time() - cls_start_time

    y_cls_train_pred = crop_model.predict(X_cls_train)
    cls_train_acc = float(accuracy_score(y_cls_train, y_cls_train_pred))

    y_cls_test_pred = crop_model.predict(X_cls_test)
    cls_val_acc = float(accuracy_score(y_cls_test, y_cls_test_pred))

    crop_model_path = get_model_path('crop_model.pkl')
    joblib.dump(crop_model, crop_model_path, compress=3)
    crop_model_size_mb = os.path.getsize(crop_model_path) / (1024 * 1024)

    # --- 4. Train Yield Regression Model (XGBRegressor) ---
    df['soil_encoded'] = df['Soil_Type'].astype(str).str.strip().map(lambda s: soil_encoder_map.get(s, 0))
    df['water_encoded'] = df['Water_Availability'].astype(str).str.strip().str.lower().map(lambda w: WATER_AVAIL_MAP.get(w, 2))

    reg_feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'Kharif', 'Rabi', 'Zaid', 'crop_encoded', 'soil_encoded', 'water_encoded']
    X_reg = df[reg_feature_cols]
    y_reg = df['Expected_Yield']

    X_reg_train, X_reg_test, y_reg_train, y_reg_test = train_test_split(
        X_reg, y_reg, test_size=0.15, random_state=42
    )

    yield_model = XGBRegressor(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    )

    reg_start_time = time.time()
    yield_model.fit(X_reg_train, y_reg_train)
    reg_train_time = time.time() - reg_start_time

    y_reg_train_pred = yield_model.predict(X_reg_train)
    reg_train_r2 = float(r2_score(y_reg_train, y_reg_train_pred))

    y_reg_test_pred = yield_model.predict(X_reg_test)
    reg_val_r2 = float(r2_score(y_reg_test, y_reg_test_pred))
    reg_val_mae = float(mean_absolute_error(y_reg_test, y_reg_test_pred))

    yield_model_path = get_model_path('yield_model.pkl')
    joblib.dump(yield_model, yield_model_path, compress=3)
    yield_model_size_mb = os.path.getsize(yield_model_path) / (1024 * 1024)

    # Print summary metrics
    print("\n==================================================")
    print("      XGBoost Model Training & Evaluation Results  ")
    print("==================================================")
    print(f"Crop Classifier Training Accuracy  : {cls_train_acc * 100:.2f}%")
    print(f"Crop Classifier Validation Accuracy: {cls_val_acc * 100:.2f}%")
    print(f"Crop Classifier Training Time      : {cls_train_time:.2f} seconds")
    print(f"Crop Model File Size               : {crop_model_size_mb:.2f} MB")
    print("--------------------------------------------------")
    print(f"Yield Regressor Training R² Score  : {reg_train_r2:.4f}")
    print(f"Yield Regressor Validation R² Score: {reg_val_r2:.4f}")
    print(f"Yield Regressor Validation MAE     : {reg_val_mae:.2f} kg/ha")
    print(f"Yield Regressor Training Time      : {reg_train_time:.2f} seconds")
    print(f"Yield Model File Size              : {yield_model_size_mb:.2f} MB")
    print("==================================================\n")

    # --- 5. Write Model Metadata ---
    now = datetime.datetime.now()
    ds_mtime = get_file_mtime(dataset_path)
    ds_mtime_str = datetime.datetime.fromtimestamp(ds_mtime).isoformat() if ds_mtime else ""

    metadata = {
        "model_version": "2.0.0",
        "algorithm": "XGBoost",
        "last_trained_date": now.strftime("%Y-%m-%d %H:%M:%S"),
        "training_timestamp": time.time(),
        "dataset_name": "Crop_recommendation_extended.csv",
        "dataset_hash": compute_file_hash(dataset_path),
        "dataset_modified_date": ds_mtime_str,
        "dataset_modified_timestamp": ds_mtime,
        "total_samples": len(df),
        "crop_classifier_train_accuracy": round(cls_train_acc, 4),
        "crop_classifier_accuracy": round(cls_val_acc, 4),
        "yield_regressor_train_r2": round(reg_train_r2, 4),
        "yield_regressor_r2": round(reg_val_r2, 4),
        "yield_regressor_mae": round(reg_val_mae, 2),
        "crop_classifier_training_time_sec": round(cls_train_time, 2),
        "yield_regressor_training_time_sec": round(reg_train_time, 2),
        "crop_model_size_mb": round(crop_model_size_mb, 2),
        "yield_model_size_mb": round(yield_model_size_mb, 2)
    }

    save_json(metadata, get_model_path('model_metadata.json'))
    print("[ML Trainer] Models trained and saved successfully.")
    return metadata

if __name__ == '__main__':
    train_all_models()
