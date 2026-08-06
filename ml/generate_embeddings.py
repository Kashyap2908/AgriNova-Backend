import os
import json
import numpy as np
import tensorflow as tf
import faiss
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.absolute()
DATASET_DIR = BASE_DIR / 'PlantDiseaseImages'
EMBEDDINGS_DIR = BASE_DIR / 'embeddings'

# Ensure embeddings directory exists
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

# EfficientNetB3 default image size
IMG_SIZE = (300, 300)

def main():
    print("Loading EfficientNetB3 model...")
    # Load pretrained model
    base_model = tf.keras.applications.EfficientNetB3(
        weights='imagenet',
        include_top=False,
        pooling='avg',
        input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3)
    )
    
    preprocess_input = tf.keras.applications.efficientnet.preprocess_input
    
    metadata = {}
    embeddings_list = []
    index_id = 0
    
    # Iterate through dataset
    classes = [d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))]
    
    for class_name in classes:
        class_dir = os.path.join(DATASET_DIR, class_name)
        images = [f for f in os.listdir(class_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"Processing class: {class_name} ({len(images)} images)")
        
        for img_name in images:
            img_path = os.path.join(class_dir, img_name)
            
            try:
                # Load and preprocess image
                img = tf.keras.utils.load_img(img_path, target_size=IMG_SIZE)
                img_array = tf.keras.utils.img_to_array(img)
                img_array = np.expand_dims(img_array, axis=0)
                img_array = preprocess_input(img_array)
                
                # Extract embedding
                embedding = base_model.predict(img_array, verbose=0)[0]
                
                # Normalize for cosine similarity
                embedding = embedding / np.linalg.norm(embedding)
                
                embeddings_list.append(embedding)
                
                metadata[str(index_id)] = {
                    "path": os.path.join(class_name, img_name).replace("\\", "/"),
                    "disease": class_name
                }
                
                index_id += 1
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                
    if not embeddings_list:
        print("No images processed. Check dataset directory.")
        return
        
    print(f"Generated {len(embeddings_list)} embeddings.")
    
    # Create FAISS index
    embeddings_array = np.array(embeddings_list).astype('float32')
    dim = embeddings_array.shape[1]
    
    # IndexFlatIP calculates inner product, which is cosine similarity for normalized vectors
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings_array)
    
    # Save index and metadata
    faiss.write_index(index, str(EMBEDDINGS_DIR / 'faiss.index'))
    
    with open(EMBEDDINGS_DIR / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print(f"Saved FAISS index and metadata to {EMBEDDINGS_DIR}")

if __name__ == '__main__':
    main()
