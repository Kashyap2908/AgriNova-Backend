import csv
from pathlib import Path

DATA_DIR = Path("d:/Sem-4/Project/AgriNova/AgriNova-Backend/ml/data")

CROPS_DATA = [
    # Crop, Season, Basal(N,P,K,S,Zn,B), Veg(N,P,K), Flow(N,P,K), pH_min, pH_max, Source
    ("Rice", "Kharif", 50,60,30,0,5,0, 35,0,0, 35,0,30, 5.5, 7.0, "ICAR-IIRR Hyderabad"),
    ("Wheat", "Rabi", 60,60,40,15,5,0, 35,0,0, 35,0,20, 6.0, 7.5, "ICAR-IARI New Delhi"),
    ("Maize", "Kharif", 45,60,40,15,5,0, 50,0,0, 35,0,20, 5.5, 7.5, "ICAR-IIMR Ludhiana"),
    ("Cotton", "Kharif", 35,60,30,15,5,0, 65,0,0, 40,0,40, 6.0, 8.0, "ICAR-CICR Nagpur"),
    ("Groundnut", "Kharif", 12.5,40,25,20,5,1, 5,0,0, 7.5,10,25, 5.5, 7.0, "ICAR-DGR Junagadh"),
    ("Sugarcane", "All", 90,80,60,20,5,0, 90,0,0, 70,0,60, 6.0, 7.5, "ICAR-SBI Coimbatore"),
    ("Potato", "Rabi", 60,80,60,15,5,1, 50,0,0, 30,0,60, 5.5, 6.5, "ICAR-CPRI Shimla"),
    ("Chickpea", "Rabi", 12,40,20,20,0,1, 5,0,0, 5,10,10, 6.0, 7.5, "ICAR-IIPR Kanpur"),
    ("Mustard", "Rabi", 45,40,20,25,5,1.5, 35,0,0, 15,0,20, 6.0, 7.5, "ICAR-DRMR Bharatpur"),
    ("Soybean", "Kharif", 12.5,40,20,20,5,0, 5,0,0, 7.5,10,20, 6.0, 7.0, "ICAR-IISR Indore"),
    ("Tomato", "All", 45,60,40,15,5,1, 45,0,0, 40,20,50, 6.0, 7.0, "ICAR-IIHR Bengaluru"),
    ("Onion", "Rabi", 35,50,35,25,5,0, 40,0,0, 35,10,35, 6.0, 7.0, "ICAR-DOGR Pune"),
    ("Chilli", "All", 35,50,35,15,5,1, 35,0,0, 40,20,40, 6.0, 7.0, "ICAR-IIHR Bengaluru"),
    ("Brinjal", "All", 35,40,30,15,5,1, 35,0,0, 30,20,30, 5.5, 6.5, "ICAR-IIHR Bengaluru"),
    ("Cabbage", "Rabi", 45,50,35,15,5,1.5, 45,0,0, 20,15,25, 6.0, 7.0, "ICAR-IIHR Bengaluru"),
    ("Cauliflower", "Rabi", 45,50,35,15,5,2.0, 45,0,0, 20,15,25, 6.0, 7.0, "ICAR-IIHR Bengaluru"),
    ("Banana", "All", 60,60,60,20,5,1, 80,0,0, 60,20,120, 6.0, 7.5, "ICAR-NRCB Trichy"),
    ("Sunflower", "Kharif", 30,40,20,20,0,2, 30,0,0, 10,10,20, 6.0, 7.5, "ICAR-DOR Hyderabad"),
    ("Tur (Pigeonpea)", "Kharif", 12,40,20,20,0,1, 5,0,0, 5,10,10, 5.5, 7.5, "ICAR-IIPR Kanpur"),
    ("Green Gram (Moong)", "Kharif", 10,35,15,15,0,0, 5,0,0, 5,5,10, 6.0, 7.5, "ICAR-IIPR Kanpur"),
    ("Black Gram (Urad)", "Kharif", 10,35,15,15,0,0, 5,0,0, 5,5,10, 6.0, 7.5, "ICAR-IIPR Kanpur"),
    ("Lentil (Masoor)", "Rabi", 10,35,15,20,0,0, 5,0,0, 5,5,10, 6.0, 7.5, "ICAR-IIPR Kanpur"),
    ("Bajra", "Kharif", 30,40,20,10,3,0, 30,0,0, 20,0,10, 6.0, 8.0, "ICAR-ICRISAT Hyderabad"),
    ("Jowar", "Kharif", 35,40,25,12,3,0, 35,0,0, 20,0,15, 6.0, 8.0, "ICAR-IIMR Hyderabad"),
    ("Garlic", "Rabi", 30,40,30,20,4,0, 35,0,0, 30,10,30, 6.0, 7.0, "ICAR-DOGR Pune"),
    ("Okra", "Kharif", 30,40,30,10,3,0, 30,0,0, 20,10,20, 6.0, 7.5, "ICAR-IIHR Bengaluru"),
    ("Cucumber", "Zaid", 25,35,25,10,2,0, 25,0,0, 20,10,15, 6.0, 7.0, "ICAR-IIVR Varanasi"),
    ("Pumpkin", "Zaid", 25,35,30,10,2,0, 25,0,0, 20,10,20, 6.0, 7.5, "ICAR-IIVR Varanasi"),
    ("Bottle Gourd", "Zaid", 25,35,30,10,2,0, 25,0,0, 20,10,20, 6.0, 7.5, "ICAR-IIVR Varanasi"),
    ("Watermelon", "Zaid", 30,40,40,10,3,0, 30,0,0, 25,10,30, 6.0, 7.0, "ICAR-CIAH Bikaner"),
    ("Muskmelon", "Zaid", 30,40,40,10,3,0, 30,0,0, 25,10,30, 6.0, 7.0, "ICAR-CIAH Bikaner"),
    ("Papaya", "All", 50,50,50,15,4,1, 60,0,0, 40,20,50, 6.0, 7.5, "ICAR-IIHR Bengaluru"),
    ("Mango", "All", 50,40,60,15,5,1, 40,0,0, 40,20,60, 5.5, 7.5, "ICAR-CISH Lucknow"),
    ("Guava", "All", 40,30,40,10,3,0.5, 40,0,0, 30,10,40, 5.5, 7.5, "ICAR-CISH Lucknow"),
    ("Pomegranate", "All", 40,40,50,15,4,1, 50,0,0, 40,20,50, 6.5, 8.0, "ICAR-NRCP Solapur"),
    ("Sesame", "Kharif", 15,25,15,10,2,0, 15,0,0, 10,0,10, 6.0, 7.5, "ICAR-IIOR Hyderabad"),
    ("Pea", "Rabi", 15,35,20,15,2,0.5, 10,0,0, 10,5,10, 6.0, 7.5, "ICAR-IIVR Varanasi"),
    ("Coriander", "Rabi", 15,25,15,10,2,0, 15,0,0, 10,0,10, 6.0, 7.5, "ICAR-NRCSS Ajmer"),
    ("Fenugreek", "Rabi", 12,25,15,10,2,0, 12,0,0, 10,0,10, 6.0, 7.5, "ICAR-NRCSS Ajmer"),
    ("Cumin", "Rabi", 15,20,15,10,2,0, 15,0,0, 10,0,10, 6.5, 8.0, "ICAR-NRCSS Ajmer"),
    ("Fennel", "Rabi", 20,25,20,10,2,0, 20,0,0, 15,0,10, 6.5, 8.0, "ICAR-NRCSS Ajmer"),
    ("Castor", "Kharif", 25,35,20,15,3,0, 25,0,0, 20,0,15, 6.0, 7.5, "ICAR-IIOR Hyderabad"),
    ("Tobacco", "Rabi", 30,40,50,15,3,0, 30,0,0, 25,0,30, 5.5, 7.0, "ICAR-CTRI Rajahmundry"),
    ("Tea", "All", 40,30,40,15,3,0, 40,0,0, 30,0,30, 4.5, 5.5, "UPASI Tea Research Institute"),
    ("Coffee", "All", 40,30,40,15,3,0, 40,0,0, 30,0,30, 5.5, 6.5, "Central Coffee Research Institute"),
    ("Turmeric", "Kharif", 40,50,60,20,4,1, 40,0,0, 40,20,60, 5.5, 7.0, "ICAR-IISR Kozhikode"),
    ("Ginger", "Kharif", 35,45,50,15,4,1, 35,0,0, 35,15,50, 5.5, 7.0, "ICAR-IISR Kozhikode"),
    ("Ragi", "Kharif", 25,30,20,10,2,0, 25,0,0, 15,0,10, 5.5, 7.5, "ICAR-IIMR Hyderabad"),
    ("Apple", "All", 40,30,50,15,3,1, 40,0,0, 30,10,40, 6.0, 7.0, "ICAR-CITH Srinagar"),
    ("Grapes", "All", 50,40,70,15,5,1, 50,0,0, 40,20,70, 6.5, 7.5, "ICAR-NRCG Pune"),
    ("Citrus", "All", 40,35,45,15,4,1, 40,0,0, 30,15,45, 6.0, 7.5, "ICAR-CCRI Nagpur"),
    ("Cardamom", "All", 30,30,40,10,2,0.5, 30,0,0, 20,10,30, 5.5, 6.5, "ICAR-IISR Kozhikode"),
    ("Black Pepper", "All", 30,30,40,10,2,0.5, 30,0,0, 20,10,30, 5.5, 6.5, "ICAR-IISR Kozhikode"),
]

# Write crop_nutrient_requirement.csv
with open(DATA_DIR / "crop_nutrient_requirement.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Crop","Season","Growth_Stage","N_kg_ha","P_kg_ha","K_kg_ha","S_kg_ha","Zn_kg_ha","B_kg_ha","Ideal_pH_Min","Ideal_pH_Max","Source"])
    for row in CROPS_DATA:
        crop, season, bN, bP, bK, bS, bZn, bB, vN, vP, vK, fN, fP, fK, phMin, phMax, src = row
        writer.writerow([crop, season, "Basal", bN, bP, bK, bS, bZn, bB, phMin, phMax, src])
        if vN > 0 or vP > 0 or vK > 0:
            writer.writerow([crop, season, "Vegetative", vN, vP, vK, 0, 0, 0, phMin, phMax, src])
        if fN > 0 or fP > 0 or fK > 0:
            writer.writerow([crop, season, "Flowering", fN, fP, fK, 0, 0, 0, phMin, phMax, src])

# Write crop_growth_stage_schedule.csv
with open(DATA_DIR / "crop_growth_stage_schedule.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Crop","Stage","Stage_Order","Days_After_Sowing","N_Split_Pct","P_Split_Pct","K_Split_Pct","Application_Method","Instructions"])
    for row in CROPS_DATA:
        crop = row[0]
        writer.writerow([crop, "Basal / At Sowing", 1, 0, 40, 100, 50, "Soil Application", "Apply at the time of land preparation / sowing."])
        writer.writerow([crop, "Active Vegetative", 2, 30, 35, 0, 25, "Top Dressing / Fertigation", "Broadcast when crop completes early vegetative stage."])
        writer.writerow([crop, "Flowering & Grain Formation", 3, 60, 25, 0, 25, "Foliar Spray / Top Dressing", "Apply during panicle initiation or flowering phase."])

# Write crop_protection_master.csv
with open(DATA_DIR / "crop_protection_master.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Crop","Category","Growth_Stage","Problem","Recommended_Product","Active_Ingredient","Application_Method","Dose_Per_Acre","Cost_Per_Unit_INR","Unit","Preventive","Weather_Trigger","Remarks"])
    for row in CROPS_DATA:
        crop = row[0]
        writer.writerow([crop, "Weed Control", "Basal / Pre-emergence", "Broadleaf & Grass Weeds", "Pendimethalin 30% EC", "Pendimethalin", "Foliar Spray", "1.0 Litre", 450, "Litre", "Yes", "High Moisture", "Spray within 48 hours of sowing."])
        writer.writerow([crop, "Pest Management", "Vegetative", "Sucking Pests & Caterpillars", "Imidacloprid 17.8% SL", "Imidacloprid", "Foliar Spray", "100 ml", 350, "Pack", "No", "High Humidity", "Spray on initial appearance of pests."])
        writer.writerow([crop, "Disease Prevention", "Flowering", "Fungal Blight & Leaf Spot", "Mancozeb 75% WP", "Mancozeb", "Foliar Spray", "500 g", 300, "Pack", "Yes", "Rainfall", "Apply preventively during overcast humid weather."])

print(f"Successfully generated datasets for {len(CROPS_DATA)} crops!")
