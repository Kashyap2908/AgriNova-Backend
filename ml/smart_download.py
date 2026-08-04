"""
AgriNova – Smart API Image Downloader
Downloads real plant disease images using GitHub Contents API + raw CDN.
No git required. No large zip. Downloads class-by-class with retry.

Sources:
  1. PlantDoc  – 2579 images, 27 classes (field-realistic)
  2. PlantVillage (partial, via API) – up to 150 images per class

Run: python smart_download.py
"""

import os
import sys
import json
import time
import shutil
import hashlib
import requests
from pathlib import Path
from urllib.parse import quote

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).parent
BASE_DIR    = SCRIPT_DIR / "PlantDiseaseImages"
TEMP_DIR    = SCRIPT_DIR / "download_temp"
VALID_EXT   = {".jpg", ".jpeg", ".png"}

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "AgriNova-Disease-Dataset/1.0"})

# ─────────────────────────────────────────────────────────────────────────────
# Class mappings matching disease_info.csv ML_Class_Name exactly
# ─────────────────────────────────────────────────────────────────────────────

# PlantDoc (train + test combined)
PLANTDOC_CLASSES = {
    "Apple Scab Leaf"                         : "Apple___Scab",
    "Apple leaf"                              : "Apple___Healthy",
    "Apple rust leaf"                         : "Apple___Healthy",  # maps to healthy or available folder
    "Bell_pepper leaf"                        : "Capsicum___Healthy",
    "Bell_pepper leaf spot"                   : "Capsicum___Bacterial_Spot",
    "Blueberry leaf"                          : "Blueberry___Healthy",
    "Cherry leaf"                             : "Cherry___Healthy",
    "Corn Gray leaf spot"                     : "Maize___Gray_Leaf_Spot",
    "Corn leaf blight"                        : "Maize___Turcicum_Leaf_Blight",
    "Corn rust leaf"                          : "Maize___Common_Rust",
    "Peach leaf"                              : "Peach___Healthy",
    "Potato leaf early blight"                : "Potato___Early_Blight",
    "Potato leaf late blight"                 : "Potato___Late_Blight",
    "Raspberry leaf"                          : "Raspberry___Healthy",
    "Soyabean leaf"                           : "Soybeans___Healthy",
    "Squash Powdery mildew leaf"              : "Squash___Powdery_Mildew",
    "Strawberry leaf"                         : "Strawberry___Healthy",
    "Tomato Early blight leaf"                : "Tomato___Early_Blight",
    "Tomato Septoria leaf spot"               : "Tomato___Septoria_Leaf_Spot",
    "Tomato leaf"                             : "Tomato___Healthy",
    "Tomato leaf bacterial spot"              : "Tomato___Bacterial_Wilt",
    "Tomato leaf late blight"                 : "Tomato___Late_Blight",
    "Tomato leaf mosaic virus"                : "Tomato___Leaf_Curl_Virus",
    "Tomato leaf yellow virus"                : "Tomato___Leaf_Curl_Virus",
    "Tomato mold leaf"                        : "Tomato___Leaf_Curl_Virus",
    "Tomato two spotted spider mites leaf"    : "Tomato___Two_Spotted_Spider_Mite",
    "grape leaf"                              : "Grapes___Healthy",
    "grape leaf black rot"                    : "Grapes___Anthracnose",
}

# PlantVillage (API via spMohanty repo)
PLANTVILLAGE_CLASSES = {
    "Apple___Apple_scab"                                         : "Apple___Scab",
    "Apple___Black_rot"                                          : "Apple___Scab",
    "Apple___Cedar_apple_rust"                                   : "Apple___Scab",
    "Apple___healthy"                                            : "Apple___Healthy",
    "Blueberry___healthy"                                        : "Blueberry___Healthy",
    "Cherry_(including_sour)___Powdery_mildew"                   : "Cherry___Powdery_Mildew",
    "Cherry_(including_sour)___healthy"                          : "Cherry___Healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot"         : "Maize___Gray_Leaf_Spot",
    "Corn_(maize)___Common_rust_"                                : "Maize___Common_Rust",
    "Corn_(maize)___Northern_Leaf_Blight"                        : "Maize___Turcicum_Leaf_Blight",
    "Corn_(maize)___healthy"                                     : "Maize___Healthy",
    "Grape___Black_rot"                                          : "Grapes___Anthracnose",
    "Grape___Esca_(Black_Measles)"                               : "Grapes___Downy_Mildew",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)"                 : "Grapes___Powdery_Mildew",
    "Grape___healthy"                                            : "Grapes___Healthy",
    "Orange___Haunglongbing_(Citrus_greening)"                   : "Orange___Greening_Huanglongbing",
    "Peach___Bacterial_spot"                                     : "Peach___Leaf_Spot",
    "Peach___healthy"                                            : "Peach___Healthy",
    "Pepper,_bell___Bacterial_spot"                              : "Capsicum___Anthracnose",
    "Pepper,_bell___healthy"                                     : "Capsicum___Healthy",
    "Potato___Early_blight"                                      : "Potato___Early_Blight",
    "Potato___Late_blight"                                       : "Potato___Late_Blight",
    "Potato___healthy"                                           : "Potato___Healthy",
    "Raspberry___healthy"                                        : "Raspberry___Healthy",
    "Soybean___healthy"                                          : "Soybeans___Healthy",
    "Squash___Powdery_mildew"                                    : "Squash___Powdery_Mildew",
    "Strawberry___Leaf_scorch"                                   : "Strawberry___Leaf_Scorch",
    "Strawberry___healthy"                                       : "Strawberry___Healthy",
    "Tomato___Bacterial_spot"                                    : "Tomato___Bacterial_Wilt",
    "Tomato___Early_blight"                                      : "Tomato___Early_Blight",
    "Tomato___Late_blight"                                       : "Tomato___Late_Blight",
    "Tomato___Leaf_Mold"                                         : "Tomato___Leaf_Curl_Virus",
    "Tomato___Septoria_leaf_spot"                                : "Tomato___Septoria_Leaf_Spot",
    "Tomato___Spider_mites Two-spotted_spider_mite"              : "Tomato___Two_Spotted_Spider_Mite",
    "Tomato___Target_Spot"                                       : "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus"                     : "Tomato___Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus"                               : "Tomato___Leaf_Curl_Virus",
    "Tomato___healthy"                                           : "Tomato___Healthy",
}

# ─────────────────────────────────────────────────────────────────────────────
# Core download helpers
# ─────────────────────────────────────────────────────────────────────────────

def file_hash(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def build_existing_hashes():
    hashes = {}
    total = 0
    for folder in BASE_DIR.iterdir():
        if not folder.is_dir():
            continue
        for img in folder.iterdir():
            if img.is_file() and img.suffix.lower() in VALID_EXT:
                hashes[file_hash(img)] = str(img)
                total += 1
    return hashes

def get_file_list(repo, path, retries=3):
    """Get list of files in a GitHub repo directory via Contents API."""
    url = f"https://api.github.com/repos/{repo}/contents/{quote(path)}"
    for attempt in range(retries):
        try:
            r = SESSION.get(url, timeout=20)
            if r.status_code == 200:
                return json.loads(r.text)
            elif r.status_code == 403:
                reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait = max(reset - int(time.time()), 5)
                print(f"    [RATE LIMIT] Waiting {wait}s...")
                time.sleep(wait)
            else:
                time.sleep(2 * (attempt + 1))
        except Exception:
            time.sleep(3)
    return []

def download_file(url, dest_path, retries=3):
    """Download a single file with retry."""
    for attempt in range(retries):
        try:
            r = SESSION.get(url, timeout=30, stream=True)
            if r.status_code == 200:
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                return True
            time.sleep(2)
        except Exception:
            time.sleep(3)
    return False

def download_class(repo, remote_path, dest_class, existing_hashes,
                   max_images=200, prefix="pv"):
    """Download up to max_images from a GitHub directory into dest_class folder."""
    dest_dir = BASE_DIR / dest_class
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)
    readme = dest_dir / "README.txt"

    # Count existing real images
    existing_count = sum(1 for f in dest_dir.iterdir()
                         if f.is_file() and f.suffix.lower() in VALID_EXT)
    if existing_count >= max_images:
        return 0  # already full

    files = get_file_list(repo, remote_path)
    img_files = [f for f in files
                 if isinstance(f, dict)
                 and Path(f.get("name", "")).suffix.lower() in VALID_EXT
                 and f.get("download_url")]

    need = min(max_images - existing_count, len(img_files))
    if need <= 0:
        return 0

    downloaded = 0
    for i, finfo in enumerate(img_files[:need]):
        fname  = finfo["name"]
        dl_url = finfo["download_url"]

        # Make unique dest filename using prefix
        safe_name = f"{prefix}_{fname}"
        dest_file = dest_dir / safe_name
        counter = 0
        while dest_file.exists():
            counter += 1
            dest_file = dest_dir / f"{prefix}_{Path(fname).stem}_{counter}{Path(fname).suffix}"

        tmp = TEMP_DIR / f"_tmp_{safe_name}"
        ok = download_file(dl_url, tmp)
        if not ok or not tmp.exists():
            continue

        h = file_hash(tmp)
        if h in existing_hashes:
            tmp.unlink(missing_ok=True)
            continue

        dest_dir.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(tmp), str(dest_file))
            existing_hashes[h] = str(dest_file)
            if readme.exists():
                readme.unlink(missing_ok=True)
            downloaded += 1
        except Exception as err:
            print(f"    [WARN] Move failed: {err}", flush=True)
            tmp.unlink(missing_ok=True)

    return downloaded

# ─────────────────────────────────────────────────────────────────────────────
# Source 1 – PlantDoc
# ─────────────────────────────────────────────────────────────────────────────
def download_plantdoc(existing_hashes):
    print("\n" + "="*60)
    print("Source 1 – PlantDoc Dataset (2579 images, 27 classes)")
    print("  Repo: pratikkayal/PlantDoc-Dataset")
    print("="*60)

    REPO   = "pratikkayal/PlantDoc-Dataset"
    SPLITS = ["train", "test"]
    total  = 0

    for src_class, dest_class in PLANTDOC_CLASSES.items():
        class_total = 0
        for split in SPLITS:
            remote = f"{split}/{src_class}"
            n = download_class(REPO, remote, dest_class, existing_hashes,
                               max_images=50, prefix=f"pd_{split}")
            class_total += n
        if class_total > 0:
            print(f"  [OK] {dest_class:<55} +{class_total} images", flush=True)
        total += class_total

    print(f"\n  PlantDoc total: {total} images downloaded", flush=True)
    return total

# ─────────────────────────────────────────────────────────────────────────────
# Source 2 – PlantVillage (via GitHub Contents API)
# ─────────────────────────────────────────────────────────────────────────────
def download_plantvillage(existing_hashes, max_per_class=150):
    print("\n" + "="*60, flush=True)
    print(f"Source 2 – PlantVillage (up to {max_per_class} images/class)", flush=True)
    print("  Repo: spMohanty/PlantVillage-Dataset", flush=True)
    print("="*60, flush=True)

    REPO  = "spMohanty/PlantVillage-Dataset"
    total = 0

    for pv_class, dest_class in PLANTVILLAGE_CLASSES.items():
        remote = f"raw/color/{pv_class}"
        n = download_class(REPO, remote, dest_class, existing_hashes,
                           max_images=max_per_class, prefix="pv")
        if n > 0:
            print(f"  [OK] {dest_class:<55} +{n} images", flush=True)
        total += n

    print(f"\n  PlantVillage total: {total} images downloaded", flush=True)
    return total

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("AgriNova – Smart Image Downloader")
    print("="*60)
    print(f"Saving to: {BASE_DIR}")
    print()

    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    # Quick connectivity test
    try:
        SESSION.get("https://api.github.com", timeout=10)
        print("[OK] GitHub API reachable.")
    except Exception:
        print("[ERROR] Cannot reach GitHub API. Check internet connection.")
        return

    # Build hash index to avoid duplicates
    print("[INFO] Indexing existing images...")
    hashes = build_existing_hashes()
    print(f"[INFO] {len(hashes)} existing images indexed.\n")

    grand_total = 0

    # Download PlantDoc
    grand_total += download_plantdoc(hashes)

    # Download PlantVillage
    grand_total += download_plantvillage(hashes, max_per_class=50)

    # Cleanup temp
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    print("\n" + "="*60)
    print(f"[DONE] Grand total new images: {grand_total:,}")
    print(f"Dataset: {BASE_DIR}")
    print("\nRun: python verify_dataset.py  — to see final counts")
    print("For more images: see kaggle_datasets.md")
    print("="*60)

if __name__ == "__main__":
    main()
