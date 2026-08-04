"""
AgriNova – Dataset Verification Script
Verifies the PlantDiseaseImages folder structure against disease_info.csv.
Generates a detailed dataset_report.csv with image counts and status.

Run: python verify_dataset.py
"""

import os
import csv
import hashlib
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DISEASE_CSV = SCRIPT_DIR / "disease_info.csv"
BASE_DIR = SCRIPT_DIR / "PlantDiseaseImages"
REPORT_CSV = SCRIPT_DIR / "dataset_report.csv"

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

def count_images(folder_path):
    """Count real images (excluding README.txt)."""
    count = 0
    for f in folder_path.iterdir():
        if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS:
            count += 1
    return count

def find_duplicates(folder_path):
    """Find duplicate images using MD5 hash."""
    hashes = {}
    duplicates = 0
    for f in folder_path.iterdir():
        if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS:
            with open(f, "rb") as fp:
                h = hashlib.md5(fp.read()).hexdigest()
            if h in hashes:
                duplicates += 1
            else:
                hashes[h] = f.name
    return duplicates

def main():
    print("AgriNova – Dataset Verification")
    print("="*60)

    if not DISEASE_CSV.exists():
        print(f"[ERROR] disease_info.csv not found: {DISEASE_CSV}")
        return

    if not BASE_DIR.exists():
        print(f"[ERROR] PlantDiseaseImages directory not found: {BASE_DIR}")
        return

    # Load disease info
    diseases = []
    with open(DISEASE_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            diseases.append(row)

    print(f"[INFO] Total entries in disease_info.csv: {len(diseases)}")
    print(f"[INFO] Checking folders in: {BASE_DIR}")
    print()

    # Verification stats
    total = len(diseases)
    folders_ok = 0
    folders_missing = 0
    folders_empty = 0        # folder exists but has 0 images
    folders_low = 0          # < 50 images
    folders_good = 0         # >= 50 images

    # By crop stats
    crop_stats = defaultdict(lambda: {"total_classes": 0, "with_images": 0, "total_images": 0})

    report_rows = []

    for d in diseases:
        crop = d["Crop_Name"]
        disease = d["Disease_Name"]
        ml_class = d["ML_Class_Name"]
        folder_path = BASE_DIR / ml_class

        crop_stats[crop]["total_classes"] += 1

        if not folder_path.exists():
            status = "MISSING_FOLDER"
            img_count = 0
            duplicates = 0
            folders_missing += 1
        else:
            img_count = count_images(folder_path)
            duplicates = find_duplicates(folder_path)

            if img_count == 0:
                status = "EMPTY_PENDING"
                folders_empty += 1
            elif img_count < 50:
                status = f"LOW_IMAGES_{img_count}"
                folders_low += 1
                crop_stats[crop]["with_images"] += 1
                crop_stats[crop]["total_images"] += img_count
            else:
                status = "OK"
                folders_good += 1
                crop_stats[crop]["with_images"] += 1
                crop_stats[crop]["total_images"] += img_count

            folders_ok += 1

        report_rows.append({
            "Crop_Name": crop,
            "Disease_Name": disease,
            "ML_Class_Name": ml_class,
            "Folder_Exists": "YES" if folder_path.exists() else "NO",
            "Image_Count": img_count,
            "Duplicate_Count": duplicates,
            "Status": status,
            "Folder_Path": str(folder_path),
        })

    # Write report CSV
    fieldnames = ["Crop_Name","Disease_Name","ML_Class_Name","Folder_Exists",
                  "Image_Count","Duplicate_Count","Status","Folder_Path"]

    with open(REPORT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_rows)

    # Print summary
    print("="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    print(f"  Total disease classes  : {total}")
    print(f"  Folders found          : {folders_ok}")
    print(f"  Folders MISSING        : {folders_missing}")
    print()
    print(f"  Empty (pending images) : {folders_empty}")
    print(f"  Low images (<50)       : {folders_low}")
    print(f"  Good images (>=50)     : {folders_good}")
    print()

    total_images = sum(r["Image_Count"] for r in report_rows)
    print(f"  Total real images      : {total_images:,}")
    print()

    # Crops with full image coverage
    covered_crops = [c for c, s in crop_stats.items() if s["with_images"] > 0]
    pending_crops = [c for c, s in crop_stats.items() if s["with_images"] == 0]

    print(f"  Crops with some images : {len(covered_crops)}")
    print(f"  Crops PENDING images   : {len(pending_crops)}")
    print()

    if pending_crops:
        print("CROPS PENDING IMAGE COLLECTION (stub folders created):")
        print("-"*60)
        for c in sorted(pending_crops):
            print(f"  • {c}")
        print()

    # Top crops by image count
    print("TOP CROPS BY IMAGE COUNT:")
    print("-"*60)
    sorted_crops = sorted(crop_stats.items(), key=lambda x: x[1]["total_images"], reverse=True)
    for crop, stats in sorted_crops[:20]:
        if stats["total_images"] > 0:
            print(f"  {crop:<35} {stats['total_images']:>6} images  ({stats['with_images']}/{stats['total_classes']} classes)")

    print()
    print(f"[INFO] Full report saved to: {REPORT_CSV}")

    # Folder name consistency check
    print()
    print("FOLDER NAME CONSISTENCY CHECK:")
    print("-"*60)
    csv_ml_classes = set(d["ML_Class_Name"] for d in diseases)
    actual_folders = set(f.name for f in BASE_DIR.iterdir() if f.is_dir())
    extra_folders = actual_folders - csv_ml_classes
    if extra_folders:
        print(f"  [WARNING] {len(extra_folders)} folders in PlantDiseaseImages NOT in disease_info.csv:")
        for f in sorted(extra_folders):
            print(f"    • {f}")
    else:
        print("  [OK] All folder names match ML_Class_Name in disease_info.csv exactly.")

    print()
    print("="*60)
    print("Verification complete.")
    if total_images > 0:
        print(f"\nDataset has {total_images:,} real images ready.")
    else:
        print("\nDataset has 0 images. Run download_images.py or download_kaggle.py to collect images.")

if __name__ == "__main__":
    main()
