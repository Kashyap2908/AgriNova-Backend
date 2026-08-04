import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, applications
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "PlantDiseaseImages")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

BATCH_SIZE = 16 # Smaller batch size for better generalization on small dataset
IMG_SIZE = (224, 224)
PHASE_1_EPOCHS = 10
PHASE_2_EPOCHS = 20

def main():
    print("AgriNova - Disease Detection Model Training (Two-Phase)")
    print("=" * 50)
    
    # 1. Load Data
    print("[INFO] Loading datasets from directory...")
    # 80% Train, 20% Val
    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR,
        validation_split=0.2,
        subset="training",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode='int'
    )
    
    val_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR,
        validation_split=0.2,
        subset="validation",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode='int'
    )
    
    class_names = train_ds.class_names
    num_classes = len(class_names)
    print(f"[INFO] Found {num_classes} classes.")
    
    # Save class indices
    class_indices = {i: name for i, name in enumerate(class_names)}
    with open(os.path.join(MODELS_DIR, 'class_indices.json'), 'w') as f:
        json.dump(class_indices, f, indent=4)
        
    # Optimize datasets
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
    
    # 2. Data Augmentation
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.2),
        layers.RandomBrightness(0.1),
    ], name="data_augmentation")
    
    # 3. Model Architecture (EfficientNetB0)
    print("[INFO] Building Phase 1 model...")
    base_model = applications.EfficientNetB0(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights='imagenet'
    )
    # Phase 1: Freeze base model
    base_model.trainable = False
    
    inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
    x = data_augmentation(inputs)
    # EfficientNet expects [0,255] which is what loads natively. No explicit rescale needed.
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    model = models.Model(inputs, outputs)
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Phase 1 Callbacks
    model_path = os.path.join(MODELS_DIR, 'disease_model.keras')
    
    # Phase 1: Train Top Layer Only
    print("\n[INFO] Starting PHASE 1 (Train Classifier Head)...")
    history_1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=PHASE_1_EPOCHS,
    )
    
    # Phase 2: Fine-Tuning
    print("\n[INFO] Starting PHASE 2 (Fine-Tuning Base Model)...")
    base_model.trainable = True
    
    # Freeze all layers EXCEPT the last 30
    for layer in base_model.layers[:-30]:
        layer.trainable = False
        
    # Recompile with very low learning rate
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    callbacks = [
        ModelCheckpoint(model_path, save_best_only=True, monitor='val_accuracy', mode='max', verbose=1),
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-7, verbose=1)
    ]
    
    history_2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=PHASE_2_EPOCHS,
        callbacks=callbacks
    )
    
    # Combine History
    acc = history_1.history['accuracy'] + history_2.history['accuracy']
    val_acc = history_1.history['val_accuracy'] + history_2.history['val_accuracy']
    loss = history_1.history['loss'] + history_2.history['loss']
    val_loss = history_1.history['val_loss'] + history_2.history['val_loss']
    
    # 6. Evaluation
    print("\n[INFO] Evaluating Final Model on Validation Set...")
    test_loss, test_acc = model.evaluate(val_ds)
    print(f"Validation Accuracy: {test_acc:.4f}, Validation Loss: {test_loss:.4f}")
    
    metrics = {
        "test_accuracy": float(test_acc),
        "test_loss": float(test_loss),
        "final_train_acc": float(acc[-1]),
        "final_val_acc": float(val_acc[-1])
    }
    with open(os.path.join(MODELS_DIR, 'training_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)
        
    # Plot Training History
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(acc, label='Train Acc')
    plt.plot(val_acc, label='Val Acc')
    plt.axvline(x=PHASE_1_EPOCHS-1, color='r', linestyle='--', label='Phase 2 Start')
    plt.legend()
    plt.title('Accuracy')
    plt.subplot(1, 2, 2)
    plt.plot(loss, label='Train Loss')
    plt.plot(val_loss, label='Val Loss')
    plt.axvline(x=PHASE_1_EPOCHS-1, color='r', linestyle='--', label='Phase 2 Start')
    plt.legend()
    plt.title('Loss')
    plt.savefig(os.path.join(MODELS_DIR, 'training_history.png'))
    plt.close()
    
    # Predictions
    print("[INFO] Generating classification report and confusion matrix...")
    y_true = []
    y_pred = []
    
    # Get unshuffled validation data for accurate metrics
    val_ds_unshuffled = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR, validation_split=0.2, subset="validation", seed=42, 
        image_size=IMG_SIZE, batch_size=BATCH_SIZE, shuffle=False
    )
    
    for images, labels in val_ds_unshuffled:
        preds = model.predict(images, verbose=0)
        y_pred.extend(np.argmax(preds, axis=-1))
        y_true.extend(labels.numpy())
        
    report = classification_report(y_true, y_pred, labels=np.arange(num_classes), target_names=class_names, zero_division=0)
    with open(os.path.join(MODELS_DIR, 'classification_report.txt'), 'w') as f:
        f.write(report)
        
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(14, 12))
    sns.heatmap(cm, annot=False, cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig(os.path.join(MODELS_DIR, 'confusion_matrix.png'))
    plt.close()

    print("[INFO] Training Complete! All artifacts saved to ml/models/")

if __name__ == '__main__':
    main()
