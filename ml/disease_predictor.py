import os
import json
import csv
import numpy as np
import tensorflow as tf
import sys
from . import faiss
sys.modules['faiss'] = faiss
import shutil
import hashlib
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.absolute()
MODELS_DIR = BASE_DIR / 'models'
MODEL_PATH = MODELS_DIR / 'disease_model.keras'
CLASS_INDICES_PATH = MODELS_DIR / 'class_indices.json'
CSV_PATH = BASE_DIR / 'disease_info.csv'
EMBEDDINGS_DIR = BASE_DIR / 'embeddings'
FAISS_INDEX_PATH = EMBEDDINGS_DIR / 'faiss.index'
FAISS_METADATA_PATH = EMBEDDINGS_DIR / 'metadata.json'
SIMILAR_CACHE_DIR = BASE_DIR.parent / 'agrinova' / 'media' / 'similar_cache'
os.makedirs(SIMILAR_CACHE_DIR, exist_ok=True)
IMG_SIZE = (224, 224)

class DiseasePredictor:
    def __init__(self):
        self.model = None
        self.class_indices = {}
        self.disease_db = {}
        self.faiss_index = None
        self.faiss_metadata = {}
        self.feature_extractor = None
        
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
                    
        if self.faiss_index is None:
            if FAISS_INDEX_PATH.exists():
                self.faiss_index = faiss.read_index(str(FAISS_INDEX_PATH))
            else:
                print(f"Warning: FAISS index not found at {FAISS_INDEX_PATH}")
                
        if not self.faiss_metadata:
            if FAISS_METADATA_PATH.exists():
                with open(FAISS_METADATA_PATH, 'r') as f:
                    self.faiss_metadata = json.load(f)
                    
        if self.feature_extractor is None:
            self.feature_extractor = tf.keras.applications.EfficientNetB3(
                weights='imagenet',
                include_top=False,
                pooling='avg',
                input_shape=(300, 300, 3)
            )

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
        
        # Similarity Search
        similarity_score = 0
        similar_disease = None
        similar_image_url = None
        
        if self.faiss_index is not None and self.feature_extractor is not None:
            try:
                sim_img = tf.keras.utils.load_img(image_path, target_size=(300, 300))
                sim_img_array = tf.keras.utils.img_to_array(sim_img)
                sim_img_array = np.expand_dims(sim_img_array, axis=0)
                sim_img_array = tf.keras.applications.efficientnet.preprocess_input(sim_img_array)
                
                embedding = self.feature_extractor.predict(sim_img_array, verbose=0)[0]
                embedding = embedding / np.linalg.norm(embedding)
                embedding = np.expand_dims(embedding, axis=0).astype('float32')
                
                D, I = self.faiss_index.search(embedding, 1)
                
                if len(I) > 0 and len(I[0]) > 0:
                    idx_str = str(I[0][0])
                    raw_sim = float(D[0][0])
                    
                    # Scale raw cosine similarity (typically 0.4-0.7 for same class) to user-friendly 0-100%
                    if raw_sim >= 0.65:
                        similarity_score = 90.0 + min(10.0, (raw_sim - 0.65) * 30.0)
                    elif raw_sim >= 0.5:
                        similarity_score = 80.0 + (raw_sim - 0.5) * 66.6
                    else:
                        similarity_score = raw_sim * 160.0
                        
                    similarity_score = min(100.0, similarity_score)
                    
                    if idx_str in self.faiss_metadata:
                        meta = self.faiss_metadata[idx_str]
                        similar_disease = meta["disease"]
                        
                        orig_path = BASE_DIR / 'PlantDiseaseImages' / meta["path"]
                        if orig_path.exists():
                            file_ext = orig_path.suffix
                            file_hash = hashlib.md5(str(orig_path).encode()).hexdigest()
                            cache_filename = f"{file_hash}{file_ext}"
                            cache_filepath = SIMILAR_CACHE_DIR / cache_filename
                            
                            if not cache_filepath.exists():
                                shutil.copy2(orig_path, cache_filepath)
                                
                            similar_image_url = f"/media/similar_cache/{cache_filename}"
            except Exception as e:
                print(f"Error in similarity search: {e}")
        
        # Threshold Check for Invalid/Non-Leaf Images
        if confidence < 40.0 and similarity_score < 80.0:
            return {
                "error": "Invalid Image Detected",
                "message": "Unable to confidently identify the disease. Please upload a clearer leaf image."
            }
            
        verification_status = "Unverified"
        if similarity_score >= 90.0:
            if similar_disease == predicted_ml_class:
                verification_status = "Verified Prediction (High Confidence)"
            else:
                verification_status = "Unverified Prediction (Medium Confidence)"
        elif similarity_score >= 80.0:
            verification_status = "Model Prediction Used (Medium Confidence)"
        else:
            verification_status = "Model Prediction Used"
        
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
            
        # Append similarity details
        response["similar_image_url"] = similar_image_url
        response["similarity_score"] = f"{similarity_score:.1f}%" if similarity_score > 0 else "N/A"
        response["verification_status"] = verification_status
        response["classifier_confidence"] = f"{confidence:.2f}%"
            
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
