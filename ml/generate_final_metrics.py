import os
import json
import hashlib
import time
import requests
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, accuracy_score
from pathlib import Path

# Fix relative imports for predictor
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from disease_predictor import DiseasePredictor

BASE_DIR = Path(__file__).parent.absolute()
MODELS_DIR = BASE_DIR / 'models'
MODEL_PATH = MODELS_DIR / 'disease_model.keras'
DATA_DIR = BASE_DIR / 'PlantDiseaseImages'
IMG_SIZE = (224, 224)
BATCH_SIZE = 16

def get_file_info(filepath):
    """Returns SHA256 and last modified time of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            
    mtime = os.path.getmtime(filepath)
    mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
    
    return sha256_hash.hexdigest(), mod_time

def evaluate_metrics():
    print("="*50)
    print("1 & 2. FINAL EVALUATION METRICS")
    print("="*50)
    
    model = tf.keras.models.load_model(str(MODEL_PATH))
    
    val_ds_unshuffled = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR, validation_split=0.2, subset="validation", seed=42, 
        image_size=IMG_SIZE, batch_size=BATCH_SIZE, shuffle=False
    )
    
    class_names = val_ds_unshuffled.class_names
    num_classes = len(class_names)
    
    y_true = []
    y_pred_probs = []
    
    for images, labels in val_ds_unshuffled:
        preds = model.predict(images, verbose=0)
        y_pred_probs.extend(preds)
        y_true.extend(labels.numpy())
        
    y_pred_probs = np.array(y_pred_probs)
    y_true = np.array(y_true)
    
    # Calculate Top-1, Top-3, Top-5
    top1 = 0
    top3 = 0
    top5 = 0
    n = len(y_true)
    
    y_pred_classes = []
    
    for i in range(n):
        true_label = y_true[i]
        probs = y_pred_probs[i]
        
        sorted_indices = np.argsort(probs)[::-1]
        y_pred_classes.append(sorted_indices[0])
        
        if true_label == sorted_indices[0]: top1 += 1
        if true_label in sorted_indices[:3]: top3 += 1
        if true_label in sorted_indices[:5]: top5 += 1
        
    print(f"Test (Top-1) Accuracy : {(top1/n)*100:.2f}%")
    print(f"Top-3 Accuracy        : {(top3/n)*100:.2f}%")
    print(f"Top-5 Accuracy        : {(top5/n)*100:.2f}%")
    
    report_dict = classification_report(y_true, y_pred_classes, labels=np.arange(num_classes), target_names=class_names, zero_division=0, output_dict=True)
    report_str = classification_report(y_true, y_pred_classes, labels=np.arange(num_classes), target_names=class_names, zero_division=0)
    
    # Overwrite the broken one
    with open(MODELS_DIR / 'classification_report.txt', 'w') as f:
        f.write(report_str)
        
    print(f"Macro Precision       : {report_dict['macro avg']['precision']:.4f}")
    print(f"Macro Recall          : {report_dict['macro avg']['recall']:.4f}")
    print(f"Macro F1 Score        : {report_dict['macro avg']['f1-score']:.4f}")

def test_external_images():
    print("\n"+"="*50)
    print("4. EXTERNAL IMAGE TESTS")
    print("="*50)
    
    external_urls = {
        "Apple": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Apple_leaf.jpg/320px-Apple_leaf.jpg",
        "Capsicum": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Capsicum_annuum_leaf.jpg/320px-Capsicum_annuum_leaf.jpg",
        "Tomato": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Tomato_leaf.jpg/320px-Tomato_leaf.jpg",
        "Potato": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Potato_leaf.jpg/320px-Potato_leaf.jpg"
    }
    
    predictor = DiseasePredictor()
    os.makedirs(BASE_DIR / 'temp_external', exist_ok=True)
    
    for crop, url in external_urls.items():
        try:
            res = requests.get(url, headers={'User-Agent': 'AgriNovaTestBot/1.0 (test@example.com)'})
            if res.status_code != 200:
                print(f"Failed to download {crop}, status: {res.status_code}")
                continue
                
            img_path = BASE_DIR / 'temp_external' / f'{crop}.jpg'
            with open(img_path, 'wb') as f:
                f.write(res.content)
                
            prediction = predictor.predict_disease(str(img_path))
            
            print(f"Actual Crop       : {crop}")
            print(f"Predicted Crop    : {prediction.get('crop')}")
            print(f"Predicted Disease : {prediction.get('disease')}")
            print(f"Confidence        : {prediction.get('confidence')}")
            print("-" * 30)
            
        except Exception as e:
            print(f"Failed to test {crop}: {e}")

def print_model_info():
    print("\n"+"="*50)
    print("5. MODEL VERIFICATION")
    print("="*50)
    
    sha256, mtime = get_file_info(MODEL_PATH)
    print(f"Model Path        : {MODEL_PATH}")
    print(f"Last Modified     : {mtime}")
    print(f"SHA256 Hash       : {sha256}")

if __name__ == "__main__":
    evaluate_metrics()
    test_external_images()
    print_model_info()
