"""
AgriNova – Image Organizer Script
Organizes images from any downloaded dataset into the correct PlantDiseaseImages folders.

Usage:
  python organize_images.py                                         # Auto-scan download_temp
  python organize_images.py --source <path_to_dataset_folder>     # Specific folder
  python organize_images.py --source <path> --dry-run             # Preview without copying

Features:
  - Hash-based deduplication
  - Laplacian variance blur detection
  - Removes placeholder README.txt when real images added
  - Generates mapping report
"""

import os
import csv
import shutil
import hashlib
import argparse
from pathlib import Path

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

SCRIPT_DIR = Path(__file__).parent
DISEASE_CSV = SCRIPT_DIR / "disease_info.csv"
BASE_DIR = SCRIPT_DIR / "PlantDiseaseImages"
DOWNLOAD_TEMP = SCRIPT_DIR / "download_temp"

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
BLUR_THRESHOLD = 100  # Laplacian variance below this → blurry

# ─────────────────────────────────────────────────────────────────────────────
# Folder name normalization (converts any naming convention → AgriNova format)
# ─────────────────────────────────────────────────────────────────────────────
def normalize_class_name(name):
    """Normalize a folder name to AgriNova ML_Class_Name format."""
    return (name.strip().title()
            .replace(" (", "_").replace("(", "").replace(")", "")
            .replace("/", "_").replace(" ", "_").replace("-", "_")
            .replace("'", "").replace(",", "").replace(".", "")
            .replace("__", "_"))

def load_valid_classes():
    """Load all valid ML_Class_Names from disease_info.csv."""
    classes = {}
    with open(DISEASE_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            classes[row["ML_Class_Name"]] = row["Image_Folder_Name"]
    return classes

def file_hash(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def is_blurry(path):
    if not HAS_CV2:
        return False
    try:
        img = cv2.imread(str(path))
        if img is None:
            return True
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        return variance < BLUR_THRESHOLD
    except Exception:
        return False

def find_best_match(folder_name, valid_classes):
    """Find the best AgriNova class name for a given folder name."""
    # Exact match
    if folder_name in valid_classes:
        return folder_name

    # Normalized match
    norm = normalize_class_name(folder_name)
    if norm in valid_classes:
        return norm

    # Partial match – try splitting on ___ separator
    parts = folder_name.replace("___", "||").split("||")
    if len(parts) == 2:
        crop_part, disease_part = parts
        crop_norm = normalize_class_name(crop_part)
        disease_norm = normalize_class_name(disease_part)
        candidate = f"{crop_norm}___{disease_norm}"
        if candidate in valid_classes:
            return candidate

    # Fuzzy partial – check if folder name contains a valid class substring
    folder_lower = folder_name.lower()
    for vc in valid_classes:
        if folder_lower in vc.lower() or vc.lower() in folder_lower:
            return vc

    return None

def organize_folder(source_dir, valid_classes, dry_run=False, existing_hashes=None):
    """Organize images from source_dir into PlantDiseaseImages."""
    if existing_hashes is None:
        existing_hashes = {}

    stats = {
        "total_found": 0,
        "copied": 0,
        "skipped_no_match": 0,
        "skipped_duplicate": 0,
        "skipped_blurry": 0,
        "skipped_exists": 0,
    }
    unmatched_folders = set()

    for item in source_dir.rglob("*"):
        if not item.is_dir():
            continue
        # Check if this folder is a disease class folder
        match = find_best_match(item.name, valid_classes)
        if not match:
            # Check parent directory name
            match = find_best_match(item.parent.name, valid_classes)

        if not match:
            # Collect images inside for reporting
            has_images = any(
                f.suffix.lower() in VALID_EXTENSIONS
                for f in item.iterdir() if f.is_file()
            )
            if has_images:
                unmatched_folders.add(item.name)
            continue

        dest_dir = BASE_DIR / match
        dest_dir.mkdir(parents=True, exist_ok=True)
        readme = dest_dir / "README.txt"

        for img_file in item.iterdir():
            if not img_file.is_file() or img_file.suffix.lower() not in VALID_EXTENSIONS:
                continue
            stats["total_found"] += 1

            # Blur check
            if is_blurry(img_file):
                stats["skipped_blurry"] += 1
                continue

            # Duplicate check
            h = file_hash(img_file)
            if h in existing_hashes:
                stats["skipped_duplicate"] += 1
                continue

            dest_file = dest_dir / img_file.name
            if dest_file.exists():
                stats["skipped_exists"] += 1
                continue

            if not dry_run:
                shutil.copy2(img_file, dest_file)
                if readme.exists():
                    readme.unlink()
                existing_hashes[h] = str(dest_file)

            stats["copied"] += 1

    return stats, unmatched_folders

def build_existing_hashes():
    """Build hash index of all existing images to avoid duplicates."""
    print("[INFO] Building hash index of existing images...")
    hashes = {}
    total = 0
    for folder in BASE_DIR.iterdir():
        if folder.is_dir():
            for img in folder.iterdir():
                if img.is_file() and img.suffix.lower() in VALID_EXTENSIONS:
                    h = file_hash(img)
                    hashes[h] = str(img)
                    total += 1
    print(f"[INFO] Indexed {total:,} existing images.")
    return hashes

def main():
    parser = argparse.ArgumentParser(description="AgriNova Image Organizer")
    parser.add_argument("--source", type=str, default=None,
                        help="Source directory to scan for images")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without copying")
    args = parser.parse_args()

    print("AgriNova – Image Organizer")
    print("="*60)

    if not DISEASE_CSV.exists():
        print(f"[ERROR] disease_info.csv not found.")
        return

    valid_classes = load_valid_classes()
    print(f"[INFO] Loaded {len(valid_classes)} valid ML classes from disease_info.csv")

    if args.dry_run:
        print("[MODE] DRY RUN – no files will be copied")

    # Determine source directory
    if args.source:
        source = Path(args.source)
        if not source.exists():
            print(f"[ERROR] Source directory not found: {source}")
            return
        sources = [source]
    else:
        # Auto-scan download_temp
        if not DOWNLOAD_TEMP.exists():
            print(f"[INFO] No download_temp directory found at: {DOWNLOAD_TEMP}")
            print("       Specify a source with: --source <path>")
            return
        sources = [DOWNLOAD_TEMP]

    # Build existing hash index
    existing_hashes = build_existing_hashes()

    # Process each source
    total_copied = 0
    all_unmatched = set()

    for source_dir in sources:
        print(f"\n[PROCESSING] {source_dir}")
        stats, unmatched = organize_folder(source_dir, valid_classes,
                                            dry_run=args.dry_run,
                                            existing_hashes=existing_hashes)
        all_unmatched.update(unmatched)
        total_copied += stats["copied"]

        print(f"  Found    : {stats['total_found']:,} images")
        print(f"  Copied   : {stats['copied']:,}")
        print(f"  Duplicates: {stats['skipped_duplicate']:,}")
        print(f"  Blurry   : {stats['skipped_blurry']:,}")
        print(f"  Exists   : {stats['skipped_exists']:,}")
        print(f"  No match : {stats['skipped_no_match']:,}")

    if all_unmatched:
        print(f"\n[WARNING] {len(all_unmatched)} unmatched source folders:")
        for f in sorted(all_unmatched):
            print(f"  • {f}")

    print(f"\n{'='*60}")
    print(f"[COMPLETE] Total images organized: {total_copied:,}")
    if not args.dry_run:
        print(f"Run verify_dataset.py to check updated counts.")

if __name__ == "__main__":
    main()
