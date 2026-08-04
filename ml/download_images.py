"""
AgriNova – Real Image Downloader (Robust Multi-Source)
Downloads real plant disease images from publicly accessible sources.

Strategy 1: PlantDoc dataset (GitHub, ~50 MB, 2579 images, 27 classes)
            Field-realistic images. Full git clone — fast.
Strategy 2: PlantVillage via git sparse-checkout
            Downloads only raw/color/ (~1.5 GB) instead of full 2.5 GB repo.
Strategy 3: PlantVillage per-file API download (fallback)
            Downloads images file-by-file via GitHub raw CDN with retry.

Run: python download_images.py
"""

import os
import shutil
import subprocess
import sys
import time
import hashlib
import json
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR / "PlantDiseaseImages"
DOWNLOAD_TEMP = SCRIPT_DIR / "download_temp"
VALID_EXT = {".jpg", ".jpeg", ".png"}

# ─────────────────────────────────────────────────────────────────────────────
# PlantVillage → AgriNova folder mapping
# ─────────────────────────────────────────────────────────────────────────────
PLANTVILLAGE_MAP = {
    "Apple___Apple_scab"                                        : "Apple___Apple_Scab",
    "Apple___Black_rot"                                         : "Apple___Black_Rot",
    "Apple___Cedar_apple_rust"                                  : "Apple___Cedar_Apple_Rust",
    "Apple___healthy"                                           : "Apple___Healthy",
    "Blueberry___healthy"                                       : "Blueberry___Healthy",
    "Cherry_(including_sour)___Powdery_mildew"                  : "Cherry___Powdery_Mildew",
    "Cherry_(including_sour)___healthy"                         : "Cherry___Healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot"        : "Maize___Gray_Leaf_Spot",
    "Corn_(maize)___Common_rust_"                               : "Maize___Common_Rust",
    "Corn_(maize)___Northern_Leaf_Blight"                       : "Maize___Turcicum_Leaf_Blight",
    "Corn_(maize)___healthy"                                    : "Maize___Healthy",
    "Grape___Black_rot"                                         : "Grapes___Black_Rot",
    "Grape___Esca_(Black_Measles)"                              : "Grapes___Esca_Black_Measles",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)"                : "Grapes___Leaf_Blight",
    "Grape___healthy"                                           : "Grapes___Healthy",
    "Orange___Haunglongbing_(Citrus_greening)"                  : "Orange___Greening_Huanglongbing",
    "Peach___Bacterial_spot"                                    : "Peach___Bacterial_Spot",
    "Peach___healthy"                                           : "Peach___Healthy",
    "Pepper,_bell___Bacterial_spot"                             : "Capsicum___Bacterial_Spot",
    "Pepper,_bell___healthy"                                    : "Capsicum___Healthy",
    "Potato___Early_blight"                                     : "Potato___Early_Blight",
    "Potato___Late_blight"                                      : "Potato___Late_Blight",
    "Potato___healthy"                                          : "Potato___Healthy",
    "Raspberry___healthy"                                       : "Raspberry___Healthy",
    "Soybean___healthy"                                         : "Soybeans___Healthy",
    "Squash___Powdery_mildew"                                   : "Squash___Powdery_Mildew",
    "Strawberry___Leaf_scorch"                                  : "Strawberry___Leaf_Scorch",
    "Strawberry___healthy"                                      : "Strawberry___Healthy",
    "Tomato___Bacterial_spot"                                   : "Tomato___Bacterial_Spot",
    "Tomato___Early_blight"                                     : "Tomato___Early_Blight",
    "Tomato___Late_blight"                                      : "Tomato___Late_Blight",
    "Tomato___Leaf_Mold"                                        : "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot"                               : "Tomato___Septoria_Leaf_Spot",
    "Tomato___Spider_mites Two-spotted_spider_mite"             : "Tomato___Two-Spotted_Spider_Mite",
    "Tomato___Target_Spot"                                      : "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus"                    : "Tomato___Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus"                              : "Tomato___Mosaic_Virus",
    "Tomato___healthy"                                          : "Tomato___Healthy",
}

# PlantDoc → AgriNova folder mapping
PLANTDOC_MAP = {
    "Apple Scab Leaf"                   : "Apple___Apple_Scab",
    "Apple leaf"                        : "Apple___Healthy",
    "Apple rust leaf"                   : "Apple___Cedar_Apple_Rust",
    "Bell_pepper leaf"                  : "Capsicum___Healthy",
    "Bell_pepper leaf spot"             : "Capsicum___Bacterial_Spot",
    "Blueberry leaf"                    : "Blueberry___Healthy",
    "Cherry leaf"                       : "Cherry___Healthy",
    "Corn Gray leaf spot"               : "Maize___Gray_Leaf_Spot",
    "Corn leaf blight"                  : "Maize___Turcicum_Leaf_Blight",
    "Corn rust leaf"                    : "Maize___Common_Rust",
    "Peach leaf"                        : "Peach___Healthy",
    "Potato leaf early blight"          : "Potato___Early_Blight",
    "Potato leaf late blight"           : "Potato___Late_Blight",
    "Raspberry leaf"                    : "Raspberry___Healthy",
    "Soyabean leaf"                     : "Soybeans___Healthy",
    "Squash Powdery mildew leaf"        : "Squash___Powdery_Mildew",
    "Strawberry leaf"                   : "Strawberry___Healthy",
    "Tomato Early blight leaf"          : "Tomato___Early_Blight",
    "Tomato Septoria leaf spot"         : "Tomato___Septoria_Leaf_Spot",
    "Tomato leaf"                       : "Tomato___Healthy",
    "Tomato leaf bacterial spot"        : "Tomato___Bacterial_Spot",
    "Tomato leaf late blight"           : "Tomato___Late_Blight",
    "Tomato leaf mosaic virus"          : "Tomato___Mosaic_Virus",
    "Tomato leaf yellow virus"          : "Tomato___Leaf_Curl_Virus",
    "Tomato mold leaf"                  : "Tomato___Leaf_Mold",
    "Tomato two spotted spider mites leaf" : "Tomato___Two-Spotted_Spider_Mite",
    "grape leaf"                        : "Grapes___Healthy",
    "grape leaf black rot"              : "Grapes___Black_Rot",
}

# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────
def check_git():
    try:
        r = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False

def file_hash(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def copy_images(source_dir, folder_map, existing_hashes, dry_run=False):
    """Copy images from source directory using folder_map to PlantDiseaseImages."""
    copied = 0
    for src_class, dest_class in folder_map.items():
        # Find matching source directory (check both train/ and test/)
        candidates = list(source_dir.rglob(src_class))
        candidates = [c for c in candidates if c.is_dir()]
        if not candidates:
            continue

        dest_dir = BASE_DIR / dest_class
        dest_dir.mkdir(parents=True, exist_ok=True)
        readme = dest_dir / "README.txt"

        for src_dir in candidates:
            for img in src_dir.iterdir():
                if not img.is_file() or img.suffix.lower() not in VALID_EXT:
                    continue
                h = file_hash(img)
                if h in existing_hashes:
                    continue
                dest_file = dest_dir / img.name
                counter = 0
                while dest_file.exists():
                    counter += 1
                    dest_file = dest_dir / f"{img.stem}_{counter}{img.suffix}"
                if not dry_run:
                    shutil.copy2(img, dest_file)
                    existing_hashes[h] = str(dest_file)
                    if readme.exists():
                        readme.unlink()
                copied += 1
    return copied

def build_existing_hashes():
    hashes = {}
    for folder in BASE_DIR.iterdir():
        if folder.is_dir():
            for img in folder.iterdir():
                if img.is_file() and img.suffix.lower() in VALID_EXT:
                    hashes[file_hash(img)] = str(img)
    return hashes

# ─────────────────────────────────────────────────────────────────────────────
# Strategy 1 – PlantDoc (small, ~50 MB, 2579 images, fast)
# ─────────────────────────────────────────────────────────────────────────────
def download_plantdoc(existing_hashes):
    print("\n" + "="*60)
    print("Strategy 1 – PlantDoc Dataset (GitHub, ~50 MB, 2579 images)")
    print("="*60)

    if not check_git():
        print("[WARNING] git not found. Skipping git clone strategy.")
        return 0

    dest = DOWNLOAD_TEMP / "PlantDoc"
    if dest.exists():
        print(f"[INFO] Already cloned: {dest}")
    else:
        DOWNLOAD_TEMP.mkdir(parents=True, exist_ok=True)
        print("[INFO] Cloning PlantDoc repository...")
        cmd = ["git", "clone", "--depth=1",
               "https://github.com/pratikkayal/PlantDoc-Dataset.git",
               str(dest)]
        result = subprocess.run(cmd, capture_output=False, text=True)
        if result.returncode != 0:
            print("[ERROR] git clone failed for PlantDoc.")
            return 0

    print("[INFO] Organizing PlantDoc images into AgriNova folders...")
    copied = copy_images(dest, PLANTDOC_MAP, existing_hashes)
    print(f"[SUCCESS] PlantDoc: {copied} images organized.")
    return copied

# ─────────────────────────────────────────────────────────────────────────────
# Strategy 2 – PlantVillage via git sparse-checkout
# Clones only raw/color/ subtree – avoids downloading segmented/grayscale sets
# ─────────────────────────────────────────────────────────────────────────────
def download_plantvillage_sparse(existing_hashes):
    print("\n" + "="*60)
    print("Strategy 2 – PlantVillage Sparse-Checkout (color images only)")
    print("="*60)

    if not check_git():
        print("[WARNING] git not found. Skipping sparse-checkout strategy.")
        return 0

    dest = DOWNLOAD_TEMP / "PlantVillage-sparse"

    if dest.exists() and any((dest / "raw" / "color").rglob("*.jpg")):
        print(f"[INFO] Already partially cloned: {dest}")
    else:
        DOWNLOAD_TEMP.mkdir(parents=True, exist_ok=True)
        print("[INFO] Setting up sparse-checkout for PlantVillage raw/color/...")
        print("[INFO] This downloads ~1 GB of color images. Please wait...")

        # Initialize repo, configure sparse-checkout, then fetch
        cmds = [
            ["git", "init", str(dest)],
            ["git", "-C", str(dest), "remote", "add", "origin",
             "https://github.com/spMohanty/PlantVillage-Dataset.git"],
            ["git", "-C", str(dest), "config", "core.sparseCheckout", "true"],
        ]
        for cmd in cmds:
            subprocess.run(cmd, capture_output=True)

        # Write sparse-checkout config
        sparse_file = dest / ".git" / "info" / "sparse-checkout"
        sparse_file.write_text("raw/color/\n")

        # Pull just the color folder
        print("[INFO] Fetching sparse repository (this may take several minutes)...")
        pull_cmd = ["git", "-C", str(dest), "pull", "--depth=1", "origin", "master"]
        result = subprocess.run(pull_cmd, capture_output=False, text=True)
        if result.returncode != 0:
            print("[WARNING] Sparse-checkout pull failed.")
            return 0

    # Organize images
    color_dir = dest / "raw" / "color"
    if not color_dir.exists():
        print("[WARNING] raw/color/ not found after sparse-checkout.")
        return 0

    print("[INFO] Organizing PlantVillage sparse images into AgriNova folders...")
    copied = copy_images(color_dir.parent.parent, PLANTVILLAGE_MAP, existing_hashes)
    print(f"[SUCCESS] PlantVillage sparse: {copied} images organized.")
    return copied

# ─────────────────────────────────────────────────────────────────────────────
# Strategy 3 – PlantVillage per-file API download (fallback)
# Uses GitHub Tree API + raw CDN to download files class-by-class
# ─────────────────────────────────────────────────────────────────────────────
def download_plantvillage_api(existing_hashes, max_per_class=200):
    print("\n" + "="*60)
    print(f"Strategy 3 – PlantVillage API download (up to {max_per_class}/class)")
    print("="*60)

    if not HAS_REQUESTS:
        print("[ERROR] requests library not found. Install with: pip install requests")
        return 0

    session = requests.Session()
    session.headers.update({
        "User-Agent": "AgriNova-Dataset-Builder/1.0",
        "Accept": "application/vnd.github.v3+json",
    })

    RAW_BASE = "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color"
    API_BASE = "https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color"

    total_copied = 0

    for pv_class, agri_class in PLANTVILLAGE_MAP.items():
        dest_dir = BASE_DIR / agri_class
        dest_dir.mkdir(parents=True, exist_ok=True)
        readme = dest_dir / "README.txt"

        # Count existing images
        existing = sum(1 for f in dest_dir.iterdir()
                       if f.is_file() and f.suffix.lower() in VALID_EXT)
        if existing >= max_per_class:
            print(f"  [SKIP] {agri_class}: already has {existing} images")
            continue

        # Get file list for this class
        try:
            import urllib.parse
            encoded = urllib.parse.quote(pv_class)
            url = f"{API_BASE}/{encoded}"
            resp = session.get(url, timeout=20)
            if resp.status_code != 200:
                print(f"  [SKIP] {pv_class}: API error {resp.status_code}")
                continue
            file_list = json.loads(resp.text)
        except Exception as e:
            print(f"  [SKIP] {pv_class}: {e}")
            continue

        imgs = [f for f in file_list
                if isinstance(f, dict) and f.get("name", "").lower().endswith((".jpg", ".jpeg", ".png"))]

        need = min(max_per_class - existing, len(imgs))
        if need <= 0:
            continue

        downloaded = 0
        for img_info in imgs[:need]:
            filename = img_info["name"]
            raw_url = img_info.get("download_url") or f"{RAW_BASE}/{urllib.parse.quote(pv_class)}/{filename}"

            dest_file = dest_dir / filename
            if dest_file.exists():
                continue

            for attempt in range(3):
                try:
                    r = session.get(raw_url, timeout=30, stream=True)
                    if r.status_code == 200:
                        with open(dest_file, "wb") as f:
                            for chunk in r.iter_content(8192):
                                f.write(chunk)
                        # Hash check
                        h = file_hash(dest_file)
                        if h in existing_hashes:
                            dest_file.unlink()
                        else:
                            existing_hashes[h] = str(dest_file)
                            if readme.exists():
                                readme.unlink()
                            downloaded += 1
                        break
                    time.sleep(1)
                except Exception:
                    time.sleep(2)

        total_copied += downloaded
        print(f"  [OK] {agri_class}: +{downloaded} images (total: {existing + downloaded})")

    print(f"\n[SUCCESS] PlantVillage API: {total_copied} images downloaded.")
    return total_copied

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("AgriNova – Real Image Downloader")
    print("="*60)
    print(f"Destination: {BASE_DIR}")
    print()

    # Check connectivity
    try:
        if HAS_REQUESTS:
            requests.get("https://github.com", timeout=10)
        else:
            import urllib.request
            urllib.request.urlopen("https://github.com", timeout=10)
    except Exception:
        print("[ERROR] No internet connection. Please connect and retry.")
        return

    DOWNLOAD_TEMP.mkdir(parents=True, exist_ok=True)

    # Build hash index of existing images
    print("[INFO] Indexing existing images...")
    existing_hashes = build_existing_hashes()
    print(f"[INFO] Existing images indexed: {len(existing_hashes)}")

    total = 0

    # ── Strategy 1: PlantDoc (small, fast, field-realistic) ──
    total += download_plantdoc(existing_hashes)

    # ── Strategy 2: PlantVillage sparse-checkout ──
    total += download_plantvillage_sparse(existing_hashes)

    # ── Strategy 3: PlantVillage API (if sparse-checkout got 0) ──
    if total < 100:
        print("\n[INFO] Falling back to Strategy 3: per-file API download...")
        total += download_plantvillage_api(existing_hashes, max_per_class=150)

    # Clean up temp
    print(f"\n[INFO] Cleaning up temp: {DOWNLOAD_TEMP}")
    shutil.rmtree(DOWNLOAD_TEMP, ignore_errors=True)

    print("\n" + "="*60)
    print(f"[COMPLETE] Total new images organized: {total:,}")
    print(f"Dataset directory: {BASE_DIR}")
    print("\nNext: Run verify_dataset.py to see updated counts.")
    print("For more images: see kaggle_datasets.md")
    print("="*60)

if __name__ == "__main__":
    main()
