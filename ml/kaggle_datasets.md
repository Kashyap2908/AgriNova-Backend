# AgriNova Disease Module – Kaggle Dataset Reference Guide

## Overview
This file lists all Kaggle datasets recommended for the AgriNova Disease Detection module.
Download these datasets using the Kaggle API or the Kaggle website.

---

## Setup Kaggle API Credentials

1. Go to https://www.kaggle.com → Account → API → "Create New API Token"
2. Download `kaggle.json` and place it at: `C:\Users\<YourName>\.kaggle\kaggle.json`
3. Install Kaggle CLI: `pip install kaggle`
4. Then run: `python download_kaggle.py`

---

## Dataset List (Download via Kaggle)

Run `download_kaggle.py` to download all datasets below automatically.
Alternatively, download each manually from the Kaggle website.

---

### 1. PlantVillage Dataset (Primary – 54K images, 38 classes)
- **Kaggle URL**: https://www.kaggle.com/datasets/emmarex/plantdisease
- **CLI**: `kaggle datasets download -d emmarex/plantdisease`
- **Crops**: Tomato, Potato, Apple, Maize (Corn), Grape, Strawberry, Peach, Cherry,
  Bell Pepper (Capsicum), Soybean, Squash, Raspberry, Blueberry, Orange
- **AgriNova Folders**:
  | Kaggle Class | AgriNova Folder |
  |---|---|
  | Tomato___Early_blight | Tomato___Early_Blight |
  | Tomato___Late_blight | Tomato___Late_Blight |
  | Tomato___Leaf_Mold | Tomato___Leaf_Mold |
  | Tomato___Septoria_leaf_spot | Tomato___Septoria_Leaf_Spot |
  | Tomato___Target_Spot | Tomato___Target_Spot |
  | Tomato___Tomato_Yellow_Leaf_Curl_Virus | Tomato___Leaf_Curl_Virus |
  | Tomato___Tomato_mosaic_virus | Tomato___Mosaic_Virus |
  | Tomato___Bacterial_spot | Tomato___Bacterial_Spot |
  | Tomato___Spider_mites... | Tomato___Two-Spotted_Spider_Mite |
  | Tomato___healthy | Tomato___Healthy |
  | Potato___Early_blight | Potato___Early_Blight |
  | Potato___Late_blight | Potato___Late_Blight |
  | Potato___healthy | Potato___Healthy |
  | Corn_(maize)___Common_rust_ | Maize___Common_Rust |
  | Corn_(maize)___Northern_Leaf_Blight | Maize___Turcicum_Leaf_Blight |
  | Corn_(maize)___Cercospora... | Maize___Gray_Leaf_Spot |
  | Corn_(maize)___healthy | Maize___Healthy |
  | Apple___Apple_scab | Apple___Apple_Scab |
  | Apple___Black_rot | Apple___Black_Rot |
  | Apple___Cedar_apple_rust | Apple___Cedar_Apple_Rust |
  | Apple___healthy | Apple___Healthy |
  | Grape___Black_rot | Grapes___Black_Rot |
  | Grape___Esca_(Black_Measles) | Grapes___Esca_Black_Measles |
  | Grape___Leaf_blight... | Grapes___Leaf_Blight |
  | Grape___healthy | Grapes___Healthy |
  | Strawberry___Leaf_scorch | Strawberry___Leaf_Scorch |
  | Strawberry___healthy | Strawberry___Healthy |
  | Peach___Bacterial_spot | Peach___Bacterial_Spot |
  | Peach___healthy | Peach___Healthy |
  | Pepper,_bell___Bacterial_spot | Capsicum___Bacterial_Spot |
  | Pepper,_bell___healthy | Capsicum___Healthy |
  | Orange___Haunglongbing... | Orange___Greening_Huanglongbing |
  | Blueberry___healthy | Blueberry___Healthy |
  | Cherry___Powdery_mildew | Cherry___Powdery_Mildew |
  | Cherry___healthy | Cherry___Healthy |
  | Raspberry___healthy | Raspberry___Healthy |
  | Soybean___healthy | Soybeans___Healthy |
  | Squash___Powdery_mildew | Squash___Powdery_Mildew |

---

### 2. Rice Disease Dataset (Paddy Doctor)
- **Kaggle URL**: https://www.kaggle.com/competitions/paddy-disease-classification
- **CLI**: `kaggle competitions download -c paddy-disease-classification`
- **Crops**: Rice (Paddy)
- **AgriNova Folders**:
  | Kaggle Class | AgriNova Folder |
  |---|---|
  | blast | Rice___Blast |
  | brown_spot | Rice___Brown_Spot |
  | bacterial_leaf_blight | Rice___Bacterial_Blight |
  | bacterial_leaf_streak | Rice___Bacterial_Leaf_Streak |
  | bacterial_panicle_blight | Rice___Sheath_Rot |
  | dead_heart | Rice___Dead_Heart |
  | downy_mildew | Rice___Downy_Mildew |
  | hispa | Rice___Hispa |
  | normal (healthy) | Rice___Healthy |
  | tungro | Rice___Tungro_Virus |

---

### 3. Rice Leaf Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases
- **CLI**: `kaggle datasets download -d vbookshelf/rice-leaf-diseases`
- **Crops**: Rice
- **Folders**: Rice___Blast, Rice___Brown_Spot, Rice___Bacterial_Blight, Rice___Healthy

---

### 4. Wheat Plant Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/olyadgetch/wheat-leaf-dataset
- **CLI**: `kaggle datasets download -d olyadgetch/wheat-leaf-dataset`
- **Crops**: Wheat
- **Folders**: Wheat___Yellow_Rust, Wheat___Brown_Rust, Wheat___Loose_Smut, Wheat___Healthy

---

### 5. Wheat Disease Dataset (Multiple)
- **Kaggle URL**: https://www.kaggle.com/datasets/kushagra3204/wheat-disease-dataset
- **CLI**: `kaggle datasets download -d kushagra3204/wheat-disease-dataset`
- **Crops**: Wheat
- **Folders**: Wheat___Yellow_Rust, Wheat___Septoria, Wheat___Healthy

---

### 6. Cotton Leaf Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/janmejaybhoi/cotton-disease-dataset
- **CLI**: `kaggle datasets download -d janmejaybhoi/cotton-disease-dataset`
- **Crops**: Cotton
- **Folders**: Cotton___Bacterial_Blight, Cotton___Curl_Virus, Cotton___Fusarium_Wilt, Cotton___Healthy

---

### 7. Mango Leaf Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/aryashah2k/mango-leaf-disease-dataset
- **CLI**: `kaggle datasets download -d aryashah2k/mango-leaf-disease-dataset`
- **Crops**: Mango
- **Folders**: Mango___Anthracnose, Mango___Powdery_Mildew, Mango___Die-Back, Mango___Healthy

---

### 8. Banana Leaf Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/shreyapmaher/banana-leaf-disease-detection-dataset
- **CLI**: `kaggle datasets download -d shreyapmaher/banana-leaf-disease-detection-dataset`
- **Crops**: Banana
- **Folders**: Banana___Sigatoka_Leaf_Spot, Banana___Panama_Wilt, Banana___Healthy

---

### 9. Sugarcane Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/nirmalsankalana/sugarcane-leaf-disease-dataset
- **CLI**: `kaggle datasets download -d nirmalsankalana/sugarcane-leaf-disease-dataset`
- **Crops**: Sugarcane
- **Folders**: Sugarcane___Red_Rot, Sugarcane___Smut, Sugarcane___Yellow_Leaf, Sugarcane___Healthy

---

### 10. Cassava Leaf Disease Dataset (21K images)
- **Kaggle URL**: https://www.kaggle.com/competitions/cassava-leaf-disease-classification
- **CLI**: `kaggle competitions download -c cassava-leaf-disease-classification`
- **Crops**: Cassava (Tapioca)
- **Folders**:
  | Kaggle Class | AgriNova Folder |
  |---|---|
  | 0 (Cassava Bacterial Blight) | Cassava_(Tapioca)___Bacterial_Blight |
  | 1 (Cassava Brown Streak) | Cassava_(Tapioca)___Brown_Streak_Disease |
  | 2 (Cassava Green Mottle) | Cassava_(Tapioca)___Green_Mottle |
  | 3 (Cassava Mosaic Disease) | Cassava_(Tapioca)___Cassava_Mosaic_Disease |
  | 4 (Healthy) | Cassava_(Tapioca)___Healthy |

---

### 11. Groundnut Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/smaranjitghose/corn-or-maize-leaf-disease-dataset
- **CLI**: `kaggle datasets download -d smaranjitghose/corn-or-maize-leaf-disease-dataset`
- **Crops**: Groundnut (also Maize)
- **Folders**: Groundnut___Late_Leaf_Spot, Groundnut___Early_Leaf_Spot, Groundnut___Healthy

---

### 12. Citrus Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/dtbaker/citrus-disease
- **CLI**: `kaggle datasets download -d dtbaker/citrus-disease`
- **Crops**: Lemon, Orange, Lime, Citrus
- **Folders**: Lemon___Canker, Orange___Greening_Huanglongbing, Lemon___Healthy, Orange___Healthy

---

### 13. Plant Leaf Disease MasterDataset (19 Crops, 143K images)
- **Kaggle URL**: https://www.kaggle.com/datasets/alinedobrovsky/plant-disease-classification-merged-dataset
- **CLI**: `kaggle datasets download -d alinedobrovsky/plant-disease-classification-merged-dataset`
- **Crops**: 19 crops including Rice, Wheat, Cotton, Tomato, Potato, Groundnut

---

### 14. Coffee Leaf Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/alvarole/coffee-leaves-disease
- **CLI**: `kaggle datasets download -d alvarole/coffee-leaves-disease`
- **Crops**: Coffee
- **Folders**: Coffee___Leaf_Rust, Coffee___Healthy

---

### 15. Pomegranate Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/roshii/pomegranate-disease-dataset
- **CLI**: `kaggle datasets download -d roshii/pomegranate-disease-dataset`
- **Crops**: Pomegranate
- **Folders**: Pomegranate___Bacterial_Blight, Pomegranate___Healthy

---

### 16. Papaya Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/nikitarom/papayasdataset
- **CLI**: `kaggle datasets download -d nikitarom/papayasdataset`
- **Crops**: Papaya
- **Folders**: Papaya___Anthracnose, Papaya___Ringspot_Virus, Papaya___Healthy

---

### 17. Guava Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/asadullahgalib/guava-disease-dataset
- **CLI**: `kaggle datasets download -d asadullahgalib/guava-disease-dataset`
- **Crops**: Guava
- **Folders**: Guava___Anthracnose, Guava___Phytophthora, Guava___Healthy

---

### 18. Coconut Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/rohanpatil63/coconut-leaf-disease-dataset
- **CLI**: `kaggle datasets download -d rohanpatil63/coconut-leaf-disease-dataset`
- **Crops**: Coconut
- **Folders**: Coconut___Bud_Rot, Coconut___Root_Wilt, Coconut___Healthy

---

### 19. Chilli (Capsicum/Pepper) Disease Dataset
- **Kaggle URL**: https://www.kaggle.com/datasets/rashikrahmanpritom/plant-disease-recognition-dataset
- **CLI**: `kaggle datasets download -d rashikrahmanpritom/plant-disease-recognition-dataset`
- **Crops**: Capsicum, Green Chili, Red Chili

---

### 20. Soybean Leaf Disease
- **Kaggle URL**: https://www.kaggle.com/datasets/prabhuavula/soybean-images
- **CLI**: `kaggle datasets download -d prabhuavula/soybean-images`
- **Crops**: Soybean
- **Folders**: Soybeans___Rust, Soybeans___Yellow_Mosaic_Virus, Soybeans___Healthy

---

## Additional Sources (Non-Kaggle)

### Mendeley Data
- **Rice**: https://data.mendeley.com/datasets/fwcj7stb8r/1 (Rice Leaf Disease Dataset)
- **Tomato**: https://data.mendeley.com/datasets/ngj6kkmmzs/1
- **Wheat Rust**: https://data.mendeley.com/datasets/4drtyfjtfy/1

### ICAR Public Resources
- ICAR-IISR (Sugarcane, Spices): https://www.iisr.res.in
- ICAR-CRRI (Rice): https://www.crri.nic.in
- ICAR-CICR (Cotton): https://www.cicr.org.in
- ICAR-IIMR (Maize/Millets): https://www.iimr.res.in
- ICAR-NRC Grapes: https://www.nrcgrapes.nic.in
- ICAR-CITH (Apple): https://www.cith.res.in

### GitHub Public Repositories
- https://github.com/spMohanty/PlantVillage-Dataset (PlantVillage – 54K images)
- https://github.com/AI4Bharat/PlantDoc-Dataset (PlantDoc – 2598 images, 13 crops)
- https://github.com/pratikkayal/PlantDoc-Dataset

### PlantDoc Dataset (Indian Conditions)
- 2,598 images, 13 plant species, 17 disease classes
- More relevant for Indian field conditions than PlantVillage
- GitHub: https://github.com/pratikkayal/PlantDoc-Dataset

---

## After Downloading Kaggle Datasets

Run the organize script to map them to AgriNova folders:
```
python organize_images.py --source <download_folder> --dataset <dataset_name>
```

---

## Image Count Targets

| Priority | Crops | Image Target |
|---|---|---|
| High | Rice, Wheat, Maize, Cotton, Tomato, Potato | 200–500 per class |
| High | Sugarcane, Groundnut, Soybean, Chickpea | 150–300 per class |
| Medium | Banana, Mango, Apple, Grapes, Papaya | 150–300 per class |
| Medium | Citrus group (6 crops), Guava, Pomegranate | 100–200 per class |
| Low | Remaining 200+ specialty/medicinal crops | Collect max available |
