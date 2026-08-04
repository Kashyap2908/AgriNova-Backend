import os
import json
import csv
import numpy as np
import tensorflow as tf
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.absolute()
MODELS_DIR = BASE_DIR / 'models'
MODEL_PATH = MODELS_DIR / 'disease_model.keras'
CLASS_INDICES_PATH = MODELS_DIR / 'class_indices.json'
CSV_PATH = BASE_DIR / 'disease_info.csv'
IMG_SIZE = (224, 224)

class DiseasePredictor:
    def __init__(self):
        self.model = None
        self.class_indices = {}
        self.disease_db = {}
        
    def _load_resources(self):
        """Lazy load resources to save memory if predictor is not used immediately."""
        if self.model is None:
            if not MODEL_PATH.exists():
                raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
            self.model = tf.keras.models.load_model(str(MODEL_PATH))
            
        if not self.class_indices:
            if not CLASS_INDICES_PATH.exists():
                raise FileNotFoundError(f"Class indices not found at {CLASS_INDICES_PATH}")
            with open(CLASS_INDICES_PATH, 'r') as f:
                indices = json.load(f)
                # Ensure keys are integers
                self.class_indices = {int(k): v for k, v in indices.items()}
                
        if not self.disease_db:
            if not CSV_PATH.exists():
                raise FileNotFoundError(f"Disease info CSV not found at {CSV_PATH}")
            with open(CSV_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ml_class = row['ML_Class_Name']
                    self.disease_db[ml_class] = row

    def predict_disease(self, image_path: str) -> dict:
        """
        Predicts disease from image and returns a comprehensive structured dictionary.
        """
        self._load_resources()
        
        # Load and preprocess image
        img = tf.keras.utils.load_img(image_path, target_size=IMG_SIZE)
        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0) # Create a batch
        
        # Predict
        predictions = self.model.predict(img_array, verbose=0)[0]
        predicted_class_idx = np.argmax(predictions)
        confidence = float(predictions[predicted_class_idx]) * 100
        
        # Log Top-5 predictions for debugging
        top_5_indices = np.argsort(predictions)[-5:][::-1]
        print("\n--- Top 5 Predictions ---")
        for idx in top_5_indices:
            cls_name = self.class_indices.get(int(idx), "Unknown")
            prob = float(predictions[idx]) * 100
            print(f"Class: {cls_name:<35} | Confidence: {prob:.2f}%")
        print("-------------------------\n")
        
        predicted_ml_class = self.class_indices.get(int(predicted_class_idx))
        
        # Threshold Check for Invalid/Non-Leaf Images
        if confidence < 40.0:
            return {
                "error": "Invalid Image Detected",
                "message": f"The AI confidence is too low ({confidence:.2f}%). Please ensure you are uploading a clear, focused photo of a plant leaf."
            }
        
        # Look up in database
        db_info = self.disease_db.get(predicted_ml_class, {})
        
        is_healthy = "Healthy" in predicted_ml_class
        status = "Healthy" if is_healthy else "Diseased"

        if is_healthy:
            # Format response for healthy plant
            response = {
                "crop": db_info.get("Crop_Name", predicted_ml_class.split("___")[0]).title(),
                "disease": "None (Healthy)",
                "confidence": f"{confidence:.2f}%",
                "status": status,
                "scientific_name": db_info.get("Scientific_Name", "N/A"),
                "severity": "None",
                "affected_part": "None",
                "symptoms": "Plant appears healthy with no visible signs of disease.",
                "causes": "N/A",
                "weather_conditions": "N/A",
                "organic_treatment": "N/A",
                "chemical_treatment": "N/A",
                "recommended_active_ingredient": "N/A",
                "dosage": "N/A",
                "spray_interval": "N/A",
                "prevention": db_info.get("Prevention", "Maintain regular watering and fertilization schedules."),
                "farmer_action": "Continue best farming practices. Monitor crop health regularly.",
                "recovery_possible": "N/A",
                "estimated_yield_loss": "0%",
                "government_recommendation": db_info.get("Govt_ICAR_Recommendation", "Follow standard ICAR agricultural guidelines for this crop.")
            }
        else:
            # Format response for diseased plant
            response = {
                "crop": db_info.get("Crop_Name", predicted_ml_class.split("___")[0]).title(),
                "disease": db_info.get("Disease_Name", predicted_ml_class.split("___")[1].replace("_", " ")),
                "confidence": f"{confidence:.2f}%",
                "status": status,
                "scientific_name": db_info.get("Scientific_Name", "N/A"),
                "severity": db_info.get("Severity", "N/A"),
                "affected_part": db_info.get("Affected_Plant_Part", "N/A"),
                "symptoms": db_info.get("Symptoms", "N/A"),
                "causes": db_info.get("Causes", "N/A"),
                "weather_conditions": db_info.get("Favorable_Weather", "N/A"),
                "organic_treatment": db_info.get("Organic_Treatment", "N/A"),
                "chemical_treatment": db_info.get("Chemical_Treatment", "N/A"),
                "recommended_active_ingredient": db_info.get("Recommended_Active_Ingredient", "N/A"),
                "dosage": db_info.get("Dosage", "N/A"),
                "spray_interval": db_info.get("Spray_Interval", "N/A"),
                "prevention": db_info.get("Prevention", "N/A"),
                "farmer_action": db_info.get("Immediate_Farmer_Action", "N/A"),
                "recovery_possible": db_info.get("Recovery_Possibility", "N/A"),
                "estimated_yield_loss": db_info.get("Estimated_Yield_Loss", "N/A"),
                "government_recommendation": db_info.get("Govt_ICAR_Recommendation", "N/A")
            }
            
        return response

if __name__ == '__main__':
    # Simple test execution if run directly
    import sys
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        predictor = DiseasePredictor()
        try:
            res = predictor.predict_disease(img_path)
            print(json.dumps(res, indent=2))
        except Exception as e:
            print(f"Error predicting: {e}")
    else:
        print("Please provide an image path to test the predictor.")
