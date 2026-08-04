import os
import glob
import json
from pathlib import Path

# Adjust python path so we can import disease_predictor easily
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from disease_predictor import DiseasePredictor

def validate():
    base_dir = Path(__file__).parent.absolute()
    dataset_dir = base_dir / 'PlantDiseaseImages'
    
    if not dataset_dir.exists():
        print(f"Error: Dataset not found at {dataset_dir}")
        return
        
    predictor = DiseasePredictor()
    predictor._load_resources() # Ensure model is loaded before trying to access it directly
    
    print("=" * 100)
    print(f"{'ACTUAL FOLDER (Crop___Disease)':<40} | {'PREDICTED ML CLASS':<40} | {'CONFIDENCE':<10} | {'STATUS'}")
    print("=" * 100)
    
    total = 0
    correct = 0
    
    # Loop over all folders
    folders = sorted([f for f in os.listdir(dataset_dir) if os.path.isdir(dataset_dir / f)])
    
    for folder_name in folders:
        folder_path = dataset_dir / folder_name
        
        # Grab the first image in the folder
        images = glob.glob(str(folder_path / "*.jpg")) + glob.glob(str(folder_path / "*.JPG"))
        if not images:
            continue
            
        test_img = images[0]
        
        try:
            # Replicate the internal prediction to get the exact raw ml_class string without altering API payload
            import tensorflow as tf
            import numpy as np
            
            img = tf.keras.utils.load_img(test_img, target_size=(224, 224))
            img_array = tf.keras.utils.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)
            
            preds = predictor.model.predict(img_array, verbose=0)[0]
            pred_idx = np.argmax(preds)
            conf = float(preds[pred_idx]) * 100
            
            pred_ml_class = predictor.class_indices.get(int(pred_idx), "Unknown")
            
            is_correct = (folder_name == pred_ml_class)
            
            total += 1
            if is_correct:
                correct += 1
                status = "PASS"
            else:
                status = "FAIL"
                
            print(f"{folder_name:<40} | {pred_ml_class:<40} | {conf:>6.2f}%    | {status}")
            
        except Exception as e:
            print(f"Error predicting {folder_name}: {e}")
            
    print("=" * 100)
    if total > 0:
        print(f"Overall Validation Accuracy (1 image per class): {correct}/{total} ({(correct/total)*100:.2f}%)")
    print("=" * 100)

if __name__ == "__main__":
    validate()
