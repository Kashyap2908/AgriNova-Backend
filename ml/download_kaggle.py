"""
AgriNova – Kaggle Dataset Auto-Downloader
Downloads all recommended Kaggle datasets for the Disease Detection module.
Requirements: pip install kaggle
              Place kaggle.json at C:\\Users\\<You>\\.kaggle\\kaggle.json

Run: python download_kaggle.py
"""

import os
import subprocess
import sys
import zipfile
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
KAGGLE_TEMP = SCRIPT_DIR / "kaggle_downloads"
BASE_DIR = SCRIPT_DIR / "PlantDiseaseImages"

# ─────────────────────────────────────────────────────────────────────────────
# Kaggle dataset definitions with folder mapping
# ─────────────────────────────────────────────────────────────────────────────
DATASETS = [
    {
        "name": "PlantVillage",
        "type": "dataset",
        "id": "emmarex/plantdisease",
        "folder_map": {
            "Apple___Apple_scab"                              : "Apple___Apple_Scab",
            "Apple___Black_rot"                               : "Apple___Black_Rot",
            "Apple___Cedar_apple_rust"                        : "Apple___Cedar_Apple_Rust",
            "Apple___healthy"                                 : "Apple___Healthy",
            "Blueberry___healthy"                             : "Blueberry___Healthy",
            "Cherry_(including_sour)___Powdery_mildew"        : "Cherry___Powdery_Mildew",
            "Cherry_(including_sour)___healthy"               : "Cherry___Healthy",
            "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Maize___Gray_Leaf_Spot",
            "Corn_(maize)___Common_rust_"                     : "Maize___Common_Rust",
            "Corn_(maize)___Northern_Leaf_Blight"             : "Maize___Turcicum_Leaf_Blight",
            "Corn_(maize)___healthy"                          : "Maize___Healthy",
            "Grape___Black_rot"                               : "Grapes___Black_Rot",
            "Grape___Esca_(Black_Measles)"                    : "Grapes___Esca_Black_Measles",
            "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)"      : "Grapes___Leaf_Blight",
            "Grape___healthy"                                 : "Grapes___Healthy",
            "Orange___Haunglongbing_(Citrus_greening)"        : "Orange___Greening_Huanglongbing",
            "Peach___Bacterial_spot"                          : "Peach___Bacterial_Spot",
            "Peach___healthy"                                 : "Peach___Healthy",
            "Pepper,_bell___Bacterial_spot"                   : "Capsicum___Bacterial_Spot",
            "Pepper,_bell___healthy"                          : "Capsicum___Healthy",
            "Potato___Early_blight"                           : "Potato___Early_Blight",
            "Potato___Late_blight"                            : "Potato___Late_Blight",
            "Potato___healthy"                                : "Potato___Healthy",
            "Raspberry___healthy"                             : "Raspberry___Healthy",
            "Soybean___healthy"                               : "Soybeans___Healthy",
            "Squash___Powdery_mildew"                         : "Squash___Powdery_Mildew",
            "Strawberry___Leaf_scorch"                        : "Strawberry___Leaf_Scorch",
            "Strawberry___healthy"                            : "Strawberry___Healthy",
            "Tomato___Bacterial_spot"                         : "Tomato___Bacterial_Spot",
            "Tomato___Early_blight"                           : "Tomato___Early_Blight",
            "Tomato___Late_blight"                            : "Tomato___Late_Blight",
            "Tomato___Leaf_Mold"                              : "Tomato___Leaf_Mold",
            "Tomato___Septoria_leaf_spot"                     : "Tomato___Septoria_Leaf_Spot",
            "Tomato___Spider_mites Two-spotted_spider_mite"   : "Tomato___Two-Spotted_Spider_Mite",
            "Tomato___Target_Spot"                            : "Tomato___Target_Spot",
            "Tomato___Tomato_Yellow_Leaf_Curl_Virus"          : "Tomato___Leaf_Curl_Virus",
            "Tomato___Tomato_mosaic_virus"                    : "Tomato___Mosaic_Virus",
            "Tomato___healthy"                                : "Tomato___Healthy",
        },
    },
    {
        "name": "Rice Leaf Diseases",
        "type": "dataset",
        "id": "vbookshelf/rice-leaf-diseases",
        "folder_map": {
            "Bacterial leaf blight" : "Rice___Bacterial_Blight",
            "Brown spot"            : "Rice___Brown_Spot",
            "Leaf smut"             : "Rice___False_Smut",
        },
    },
    {
        "name": "Paddy Doctor (Rice)",
        "type": "competition",
        "id": "paddy-disease-classification",
        "folder_map": {
            "blast"                   : "Rice___Blast",
            "brown_spot"              : "Rice___Brown_Spot",
            "bacterial_leaf_blight"   : "Rice___Bacterial_Blight",
            "bacterial_leaf_streak"   : "Rice___Bacterial_Leaf_Streak",
            "bacterial_panicle_blight": "Rice___Sheath_Rot",
            "dead_heart"              : "Rice___Dead_Heart",
            "downy_mildew"            : "Rice___Downy_Mildew",
            "hispa"                   : "Rice___Hispa",
            "normal"                  : "Rice___Healthy",
            "tungro"                  : "Rice___Tungro_Virus",
        },
    },
    {
        "name": "Wheat Leaf Dataset",
        "type": "dataset",
        "id": "olyadgetch/wheat-leaf-dataset",
        "folder_map": {
            "Healthy"          : "Wheat___Healthy",
            "Yellow rust"      : "Wheat___Yellow_Rust_Stripe_Rust",
            "Brown rust"       : "Wheat___Brown_Rust_Leaf_Rust",
            "Loose smut"       : "Wheat___Loose_Smut",
        },
    },
    {
        "name": "Cotton Disease Dataset",
        "type": "dataset",
        "id": "janmejaybhoi/cotton-disease-dataset",
        "folder_map": {
            "diseased cotton leaf"  : "Cotton___Leaf_Curl_Virus",
            "diseased cotton plant" : "Cotton___Bacterial_Blight",
            "fresh cotton leaf"     : "Cotton___Healthy",
            "fresh cotton plant"    : "Cotton___Healthy",
        },
    },
    {
        "name": "Mango Leaf Disease",
        "type": "dataset",
        "id": "aryashah2k/mango-leaf-disease-dataset",
        "folder_map": {
            "Anthracnose"      : "Mango___Anthracnose",
            "Bacterial Canker" : "Mango___Bacterial_Canker",
            "Cutting Weevil"   : "Mango___Cutting_Weevil",
            "Die Back"         : "Mango___Die-Back",
            "Gall Midge"       : "Mango___Gall_Midge",
            "Healthy"          : "Mango___Healthy",
            "Powdery Mildew"   : "Mango___Powdery_Mildew",
            "Sooty Mould"      : "Mango___Sooty_Mould",
        },
    },
    {
        "name": "Banana Leaf Disease",
        "type": "dataset",
        "id": "shreyapmaher/banana-leaf-disease-detection-dataset",
        "folder_map": {
            "Cordana"          : "Banana___Cordana_Leaf_Spot",
            "Healthy"          : "Banana___Healthy",
            "Pestalotiopsis"   : "Banana___Pestalotiopsis",
            "Sigatoka"         : "Banana___Sigatoka_Leaf_Spot",
        },
    },
    {
        "name": "Sugarcane Disease",
        "type": "dataset",
        "id": "nirmalsankalana/sugarcane-leaf-disease-dataset",
        "folder_map": {
            "Healthy"          : "Sugarcane___Healthy",
            "Mosaic"           : "Sugarcane___Mosaic_Virus",
            "RedRot"           : "Sugarcane___Red_Rot",
            "Rust"             : "Sugarcane___Rust",
            "Yellow"           : "Sugarcane___Yellow_Leaf_Disease",
        },
    },
    {
        "name": "Cassava Leaf Disease (21K)",
        "type": "competition",
        "id": "cassava-leaf-disease-classification",
        "folder_map": {
            "0" : "Cassava_(Tapioca)___Bacterial_Blight",
            "1" : "Cassava_(Tapioca)___Brown_Streak_Disease",
            "2" : "Cassava_(Tapioca)___Green_Mottle",
            "3" : "Cassava_(Tapioca)___Cassava_Mosaic_Disease",
            "4" : "Cassava_(Tapioca)___Healthy",
        },
    },
    {
        "name": "Coffee Leaf Disease",
        "type": "dataset",
        "id": "alvarole/coffee-leaves-disease",
        "folder_map": {
            "healthy"      : "Coffee___Healthy",
            "rust"         : "Coffee___Coffee_Leaf_Rust",
            "miner"        : "Coffee___Leaf_Miner",
            "phoma"        : "Coffee___Phoma_Leaf_Spot",
        },
    },
    {
        "name": "Coconut Leaf Disease",
        "type": "dataset",
        "id": "rohanpatil63/coconut-leaf-disease-dataset",
        "folder_map": {
            "Bud_Rot"   : "Coconut___Bud_Rot",
            "Gray_Leaf_Spot" : "Coconut___Gray_Leaf_Spot",
            "Healthy"   : "Coconut___Healthy",
            "Leaf_Rot"  : "Coconut___Leaf_Rot",
        },
    },
    {
        "name": "Guava Disease",
        "type": "dataset",
        "id": "asadullahgalib/guava-disease-dataset",
        "folder_map": {
            "Anthracnose"      : "Guava___Anthracnose",
            "fruit_fly"        : "Guava___Fruit_Fly",
            "Healthy"          : "Guava___Healthy",
            "Phytopthora"      : "Guava___Wilt",
            "Styler_end_rot"   : "Guava___Styler_End_Rot",
        },
    },
    {
        "name": "Papaya Disease",
        "type": "dataset",
        "id": "nikitarom/papayasdataset",
        "folder_map": {
            "healthy"          : "Papaya___Healthy",
            "Anthracnose"      : "Papaya___Anthracnose",
            "Bacterial Spot"   : "Papaya___Bacterial_Spot",
            "Black Spot"       : "Papaya___Black_Spot",
            "Powdery Mildew"   : "Papaya___Powdery_Mildew",
            "Ring Spot"        : "Papaya___Ringspot_Virus",
        },
    },
    {
        "name": "Plant Disease MasterDataset (19 crops)",
        "type": "dataset",
        "id": "alinedobrovsky/plant-disease-classification-merged-dataset",
        "folder_map": {},  # Uses PlantVillage-style naming → handled by organize script
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def check_kaggle():
    try:
        result = subprocess.run(["kaggle", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Kaggle CLI found: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("[ERROR] Kaggle CLI not found. Install with: pip install kaggle")
    print("        Then place kaggle.json at: C:\\Users\\<You>\\.kaggle\\kaggle.json")
    return False

def download_dataset(ds_id, dtype, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    if dtype == "dataset":
        cmd = ["kaggle", "datasets", "download", "-d", ds_id, "-p", str(dest_dir), "--unzip"]
    elif dtype == "competition":
        cmd = ["kaggle", "competitions", "download", "-c", ds_id, "-p", str(dest_dir)]
    else:
        return False

    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode == 0

def organize_into_folders(source_dir, folder_map):
    """Copy images from source directories to AgriNova folders."""
    copied = 0
    for src_class, dest_class in folder_map.items():
        # Find matching source directory
        src_dir = None
        for d in source_dir.rglob("*"):
            if d.is_dir() and (d.name == src_class or d.name.lower() == src_class.lower()):
                src_dir = d
                break

        if not src_dir or not src_dir.exists():
            continue

        dest_dir = BASE_DIR / dest_class
        dest_dir.mkdir(parents=True, exist_ok=True)

        readme = dest_dir / "README.txt"

        for img in src_dir.rglob("*"):
            if img.is_file() and img.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp"]:
                dest_file = dest_dir / img.name
                if not dest_file.exists():
                    shutil.copy2(img, dest_file)
                    copied += 1

        if copied > 0 and readme.exists():
            readme.unlink()

    return copied

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("AgriNova – Kaggle Dataset Downloader")
    print("="*60)

    if not check_kaggle():
        sys.exit(1)

    KAGGLE_TEMP.mkdir(parents=True, exist_ok=True)
    total_copied = 0

    for ds in DATASETS:
        name = ds["name"]
        ds_id = ds["id"]
        dtype = ds["type"]
        folder_map = ds["folder_map"]

        print(f"\n{'─'*60}")
        print(f"[DOWNLOADING] {name}")
        print(f"  ID: {ds_id}")

        dest_dir = KAGGLE_TEMP / ds_id.replace("/", "_")
        ok = download_dataset(ds_id, dtype, dest_dir)

        if not ok:
            print(f"  [WARNING] Download failed for: {name}")
            continue

        if folder_map:
            print(f"  Organizing images...")
            copied = organize_into_folders(dest_dir, folder_map)
            print(f"  [OK] {copied} images organized.")
            total_copied += copied
        else:
            print(f"  [INFO] No folder map defined – images stored in {dest_dir}")

    print(f"\n{'='*60}")
    print(f"[COMPLETE] Total images organized: {total_copied}")
    print(f"Images are in: {BASE_DIR}")
    print("\nRun verify_dataset.py to check completeness.")

if __name__ == "__main__":
    main()
