"""
AgriNova – Create PlantDiseaseImages Folder Structure
Reads disease_info.csv and creates all required image folders.
Run: python create_folders.py
"""

import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DISEASE_CSV = os.path.join(SCRIPT_DIR, "disease_info.csv")
OUTPUT_BASE = os.path.join(SCRIPT_DIR, "PlantDiseaseImages")

def main():
    if not os.path.exists(DISEASE_CSV):
        print(f"[ERROR] disease_info.csv not found: {DISEASE_CSV}")
        return

    os.makedirs(OUTPUT_BASE, exist_ok=True)
    print(f"[INFO] Creating folders under: {OUTPUT_BASE}")

    folders_created = []
    folders_existing = []

    with open(DISEASE_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            folder_name = row["Image_Folder_Name"].strip()
            if not folder_name:
                continue
            folder_path = os.path.join(OUTPUT_BASE, folder_name)
            if os.path.exists(folder_path):
                folders_existing.append(folder_name)
            else:
                os.makedirs(folder_path, exist_ok=True)
                # Create a README placeholder
                readme_path = os.path.join(folder_path, "README.txt")
                crop = row["Crop_Name"]
                disease = row["Disease_Name"]
                ml_class = row["ML_Class_Name"]
                with open(readme_path, "w", encoding="utf-8") as rf:
                    rf.write(f"AgriNova PlantDiseaseImages – Placeholder\n")
                    rf.write(f"{'='*50}\n")
                    rf.write(f"Crop      : {crop}\n")
                    rf.write(f"Disease   : {disease}\n")
                    rf.write(f"ML Class  : {ml_class}\n\n")
                    if disease == "Healthy":
                        rf.write("Image requirements:\n")
                        rf.write("  - Target: 200–500 images\n")
                        rf.write("  - Clear photographs of healthy plants\n")
                        rf.write("  - Variety of lighting, angles, backgrounds\n\n")
                        rf.write("Recommended sources:\n")
                        rf.write("  - PlantVillage (GitHub/Kaggle)\n")
                        rf.write("  - Kaggle plant disease datasets\n")
                        rf.write("  - ICAR / State Agricultural University databases\n")
                    else:
                        rf.write("Image requirements:\n")
                        rf.write("  - Target: 150–500 images\n")
                        rf.write("  - Clear photographs of affected plants\n")
                        rf.write("  - Multiple disease stages\n")
                        rf.write("  - Variety of lighting, angles, backgrounds, farms\n\n")
                        rf.write("Recommended sources:\n")
                        rf.write("  - PlantVillage (GitHub/Kaggle)\n")
                        rf.write("  - Kaggle plant disease datasets\n")
                        rf.write("  - Mendeley Data\n")
                        rf.write("  - ICAR / FAO public databases\n")
                        rf.write("  - State Agricultural University (SAU) image banks\n")
                folders_created.append(folder_name)

    print(f"[SUCCESS] Folders created : {len(folders_created)}")
    print(f"[INFO]   Already existed : {len(folders_existing)}")
    print(f"[INFO]   Total folders   : {len(folders_created) + len(folders_existing)}")
    print(f"\nFolder structure ready at:\n  {OUTPUT_BASE}")

    # Write folder manifest
    manifest_path = os.path.join(SCRIPT_DIR, "folder_manifest.txt")
    all_folders = sorted(folders_created + folders_existing)
    with open(manifest_path, "w", encoding="utf-8") as mf:
        mf.write(f"AgriNova PlantDiseaseImages Folder Manifest\n")
        mf.write(f"Total folders: {len(all_folders)}\n")
        mf.write(f"{'='*60}\n")
        for f in all_folders:
            mf.write(f"{f}\n")
    print(f"[INFO] Folder manifest written: {manifest_path}")

if __name__ == "__main__":
    main()
