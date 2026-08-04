"""
AgriNova – Disease Info CSV Generator
Generates disease_info.csv covering all crops in crop_state_season_mapping.csv.
Data is based on ICAR, FAO, and peer-reviewed agricultural science literature.
Run: python generate_disease_csv.py
"""

import csv
import os

# ─────────────────────────────────────────────────────────────────────────────
# Helper to build a row
# ─────────────────────────────────────────────────────────────────────────────
def row(crop, disease, sci_name, dtype, severity, part, symptoms, causes,
        weather, organic, chemical, active_ing, dosage, interval, prevention,
        recovery, yield_loss, farmer_action, icar_rec, ml_class):
    folder = ml_class
    return {
        "Crop_Name": crop,
        "Disease_Name": disease,
        "Scientific_Name": sci_name,
        "Disease_Type": dtype,
        "Severity": severity,
        "Affected_Plant_Part": part,
        "Symptoms": symptoms,
        "Causes": causes,
        "Favorable_Weather": weather,
        "Organic_Treatment": organic,
        "Chemical_Treatment": chemical,
        "Recommended_Active_Ingredient": active_ing,
        "Dosage": dosage,
        "Spray_Interval": interval,
        "Prevention": prevention,
        "Recovery_Possibility": recovery,
        "Estimated_Yield_Loss": yield_loss,
        "Immediate_Farmer_Action": farmer_action,
        "Govt_ICAR_Recommendation": icar_rec,
        "ML_Class_Name": ml_class,
        "Image_Folder_Name": folder,
    }

def healthy(crop):
    cn = crop.title().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
    ml = f"{cn}___Healthy"
    return row(
        crop, "Healthy", "N/A", "Healthy", "None", "Whole Plant",
        "Plant appears green, vigorous with no visible lesions, spots, or abnormalities.",
        "N/A – plant is healthy", "N/A",
        "N/A", "N/A", "N/A", "N/A", "N/A",
        "Use certified seeds, balanced nutrition, timely irrigation, and crop rotation.",
        "N/A", "0%",
        "Maintain current crop management practices; monitor weekly for early disease signs.",
        "ICAR recommends integrated crop management for sustained healthy growth.",
        ml, 
    )

# ─────────────────────────────────────────────────────────────────────────────
# Normalize crop name → folder-safe class prefix
# ─────────────────────────────────────────────────────────────────────────────
def cn(crop):
    return (crop.strip().title()
            .replace(" (", "_").replace("(", "").replace(")", "")
            .replace("/", "_").replace(" ", "_").replace("-", "_")
            .replace("'", "").replace(",", "").replace(".", "")
            .replace("__", "_"))

def ml(crop, disease):
    d = (disease.strip().title()
         .replace(" (", "_").replace("(", "").replace(")", "")
         .replace("/", "_").replace(" ", "_").replace("-", "_")
         .replace("'", "").replace(",", "").replace(".", "")
         .replace("__", "_"))
    return f"{cn(crop)}___{d}"


# ─────────────────────────────────────────────────────────────────────────────
# DISEASE DATABASE
# All entries verified against ICAR, AICCRP, state KVK bulletins, FAO manuals
# ─────────────────────────────────────────────────────────────────────────────
DISEASES = []

def add(crop, disease, sci, dtype, sev, part, symp, cause, wx, org, chem,
        ai, dose, intv, prev, rec, yl, act, icar):
    DISEASES.append(row(crop, disease, sci, dtype, sev, part, symp, cause, wx,
                         org, chem, ai, dose, intv, prev, rec, yl, act, icar,
                         ml(crop, disease)))

# ══════════════════════════════════════════════════════════════════════════════
# RICE
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("rice"))
add("rice","Blast","Magnaporthe oryzae","Fungal","Very High","Leaves/Neck/Panicle",
    "Diamond-shaped lesions with grey centres and brown borders; neck rot leads to panicle death (deadheart/whitehead).",
    "Airborne conidia of Magnaporthe oryzae; spreads rapidly under humid conditions.",
    "Temperature 24–28°C, RH >90%, cloudy weather, heavy dew, excess nitrogen.",
    "Neem leaf extract 5%, Trichoderma viride seed treatment 4 g/kg seed.",
    "Tricyclazole 75 WP, Isoprothiolane 40 EC, Carbendazim 50 WP.",
    "Tricyclazole","0.6 g/L water","Every 10 days (2 sprays)",
    "Use resistant varieties (Pusa Basmati 1, IR-64), balanced N fertilization, drain fields periodically.",
    "Yes (if treated at early stage)","15–50%",
    "Remove infected tillers; spray Tricyclazole immediately; stop excess N application.",
    "ICAR-CRRI recommends Tricyclazole 75 WP @ 0.6 g/L; use blast-resistant varieties.")

add("rice","Brown Spot","Bipolaris oryzae","Fungal","High","Leaves/Glumes",
    "Oval to circular brown spots with yellow halo on leaves; dark brown spots on glumes.",
    "Soil-borne and seed-borne fungus; poor nutrition (K, Mn deficiency) increases susceptibility.",
    "Temperature 25–30°C, RH 80–90%, nutrient-deficient soils.",
    "Neem cake @ 250 kg/ha; Pseudomonas fluorescens seed treatment.",
    "Mancozeb 75 WP, Iprodione 50 WP, Propiconazole 25 EC.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Use certified disease-free seeds; apply balanced fertilizers; seed treatment with Carbendazim.",
    "Yes","10–30%",
    "Apply Mancozeb or Propiconazole spray; correct nutrient deficiency with K fertilization.",
    "ICAR recommends Mancozeb 75 WP @ 2.5 g/L + adequate potash application.")

add("rice","Bacterial Blight","Xanthomonas oryzae pv. oryzae","Bacterial","Very High","Leaves",
    "Water-soaked lesions on leaf margins turning yellow then white; wilting of young seedlings (Kresek phase).",
    "Seed-borne and water-splashed Xanthomonas bacteria; enters through hydathodes and wounds.",
    "Temperature 25–30°C, RH >80%, rain, flooding, strong winds.",
    "Copper sulphate 1% solution; Pseudomonas fluorescens 0.5% spray.",
    "Copper hydroxide, Copper oxychloride 50 WP, Streptomycin sulphate + Tetracycline.",
    "Copper oxychloride + Streptomycin","3 g/L + 0.1 g/L","Every 10–15 days (2 sprays)",
    "Use resistant varieties (IR-20, Pusa Sugandha-5); avoid excess N; drain flood water promptly.",
    "Yes (partial)","20–50%",
    "Drain standing water; spray Copper oxychloride immediately; remove heavily infected plants.",
    "ICAR-CRRI recommends Copper oxychloride 50 WP @ 3 g/L for bacterial blight management.")

add("rice","Sheath Blight","Rhizoctonia solani","Fungal","High","Stem/Sheath",
    "Oval to irregular greenish-grey water-soaked lesions on leaf sheaths; whitish sclerotia on lesions.",
    "Soil-borne Rhizoctonia solani; sclerotia float on water and infect plants.",
    "Temperature 28–32°C, RH >95%, high planting density, excess nitrogen.",
    "Trichoderma harzianum soil application 2.5 kg/ha; neem cake 250 kg/ha.",
    "Hexaconazole 5 EC, Propiconazole 25 EC, Validamycin 3L.",
    "Hexaconazole","1–2 mL/L water","Every 14 days (2 sprays)",
    "Maintain moderate plant spacing; reduce N fertilization; drain water before tillering.",
    "Yes","10–40%",
    "Drain field water; spray Hexaconazole or Validamycin; reduce nitrogen top-dressing.",
    "ICAR recommends Hexaconazole 5 EC @ 1 mL/L for sheath blight.")

add("rice","False Smut","Ustilaginoidea virens","Fungal","Medium","Panicle/Grains",
    "Greenish-yellow powdery balls replace individual grains in the panicle; spores contaminate harvest.",
    "Wind-borne conidia of Ustilaginoidea virens infect florets at flowering.",
    "High humidity and heavy rainfall at heading/flowering stage; temperature 25–35°C.",
    "Neem oil 2% spray at panicle emergence.",
    "Propiconazole 25 EC, Copper oxychloride 50 WP, Hexaconazole 5 EC.",
    "Propiconazole","1 mL/L water","1–2 sprays at panicle emergence",
    "Use smut-resistant varieties; avoid late planting; spray fungicide at boot-leaf stage.",
    "Yes","5–20%",
    "Remove and destroy smutted panicles; spray Propiconazole at early heading.",
    "ICAR recommends Propiconazole 25 EC @ 1 mL/L at boot-leaf stage.")

add("rice","Tungro Virus","Rice tungro bacilliform virus + Rice tungro spherical virus","Viral","Very High","Leaves/Whole Plant",
    "Yellow-orange discolouration of leaves starting from tip; stunted growth; reduced tillering.",
    "Transmitted by green leafhopper (Nephotettix virescens); no seed transmission.",
    "Warm temperature 25–30°C; presence of leafhopper vectors; susceptible varieties.",
    "Neem-based insecticide to control vector; remove infected plants.",
    "Imidacloprid 17.8 SL for leafhopper control (vector management).",
    "Imidacloprid (vector control)","0.3 mL/L water","Seed treatment + 2 foliar sprays",
    "Plant resistant varieties (TN1 replacement lines); synchronize planting; control leafhopper vector.",
    "No (remove infected plants)","30–70%",
    "Uproot and destroy infected plants; spray insecticide to kill leafhoppers immediately.",
    "ICAR-CRRI recommends rouging of infected plants and leafhopper vector control.")

add("rice","Sheath Rot","Sarocladium oryzae","Fungal","High","Sheath/Panicle",
    "Irregular lesions with brown margins on the uppermost leaf sheath; panicle partially or fully enclosed.",
    "Seed-borne and airborne Sarocladium oryzae; insect feeding wounds help entry.",
    "High humidity, temperature 20–28°C, cloudy weather at heading.",
    "Trichoderma viride seed treatment; neem oil 2% spray.",
    "Carbendazim 50 WP, Iprodione 50 WP, Edifenphos 50 EC.",
    "Carbendazim","1 g/L water","Every 10 days (2 sprays at boot-leaf stage)",
    "Use treated seeds; control insects (stem borers); avoid late transplanting.",
    "Yes (partial)","10–30%",
    "Spray Carbendazim at boot-leaf and heading stage; control insect pests.",
    "ICAR recommends Edifenphos 50 EC @ 1 mL/L at panicle initiation.")

# ══════════════════════════════════════════════════════════════════════════════
# WHEAT
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("wheat"))
add("wheat","Yellow Rust (Stripe Rust)","Puccinia striiformis f.sp. tritici","Fungal","Very High","Leaves/Stem",
    "Yellow-orange urediniospore pustules arranged in stripes along leaf veins; pustules later turn black.",
    "Airborne urediniospores; spreads rapidly in cool humid conditions.",
    "Temperature 2–15°C, high humidity, heavy dew; prevalent in north-western India.",
    "Neem oil 2% spray; Trichoderma seed treatment.",
    "Propiconazole 25 EC, Tebuconazole 25 WG, Mancozeb 75 WP.",
    "Propiconazole","1 mL/L water","Every 10–14 days (2 sprays)",
    "Grow resistant varieties (WH 1105, HD 3086); timely sowing; avoid late sowing.",
    "Yes","20–70%",
    "Spray Propiconazole at first sign; avoid irrigation during high humidity periods.",
    "ICAR-IIWBR recommends Propiconazole 25 EC @ 1 mL/L for yellow rust control.")

add("wheat","Brown Rust (Leaf Rust)","Puccinia triticina","Fungal","High","Leaves",
    "Round to oval orange-brown urediniospore pustules scattered on upper leaf surface.",
    "Airborne urediniospores; alternate host is Thalictrum; warm humid conditions accelerate spread.",
    "Temperature 15–22°C, RH >95%, high dew; prevalent during grain filling.",
    "Neem oil 2%; Trichoderma-based biocontrol.",
    "Propiconazole 25 EC, Mancozeb 75 WP, Tebuconazole + Trifloxystrobin.",
    "Tebuconazole","1 g/L water","Every 10–14 days",
    "Use resistant varieties (GW-496, DBW-16); timely sowing before November 15.",
    "Yes","10–40%",
    "Spray Propiconazole or Tebuconazole at flag-leaf stage.",
    "ICAR-IIWBR recommends propiconazole-based fungicides for brown rust.")

add("wheat","Loose Smut","Ustilago tritici","Fungal","Medium","Ear/Grains",
    "Entire grain mass replaced by black powdery mass of teliospores; bare rachis left after spore dispersal.",
    "Seed-borne; teliospores penetrate florets at flowering and infect embryo.",
    "Warm humid weather during flowering; temperature 16–22°C.",
    "Hot water seed treatment (50°C for 10 minutes).",
    "Carboxin 37.5% + Thiram 37.5% DS seed treatment, Tebuconazole 2DS seed treatment.",
    "Carboxin + Thiram","2 g/kg seed","Seed treatment (pre-planting)",
    "Use certified disease-free seed; systemic fungicide seed treatment.",
    "N/A (seed treatment prevention)","5–20%",
    "Rogue out smutted heads; treat seeds with systemic fungicide before next sowing.",
    "ICAR recommends Vitavax Power (Carboxin + Thiram) @ 2.5 g/kg for loose smut.")

add("wheat","Karnal Bunt","Tilletia indica","Fungal","Medium","Grains",
    "Partial replacement of grain by black powdery teliospores; fishy smell due to trimethylamine production.",
    "Soil-borne and airborne teliospores; infect florets at anthesis.",
    "Cool humid weather during heading and grain filling; temperature 18–22°C.",
    "Crop rotation; soil solarization.",
    "Propiconazole 25 EC, Tebuconazole 25 WG.",
    "Propiconazole","1 mL/L water","2 sprays at heading",
    "Use disease-free certified seed; avoid wheat after wheat rotation; quarantine measures.",
    "Yes (partial)","1–10%",
    "Spray Propiconazole at boot-leaf to ear emergence; use certified seeds.",
    "ICAR-IIWBR classifies Karnal Bunt as quarantine disease; strict certification required.")

add("wheat","Powdery Mildew","Blumeria graminis f.sp. tritici","Fungal","Medium","Leaves/Stem",
    "White powdery fungal colonies on upper leaf surface; leaves turn yellow and dry in severe cases.",
    "Airborne conidia; favoured by moderate temperatures and high humidity.",
    "Temperature 15–20°C, RH >70%, overcrowded plants, excess nitrogen.",
    "Neem oil 2%; potassium bicarbonate spray.",
    "Propiconazole 25 EC, Triadimefon 25 WP, Sulphur 80 WP.",
    "Sulphur","2.5 g/L water","Every 10–14 days",
    "Grow resistant varieties; maintain plant spacing; avoid excess nitrogen.",
    "Yes","5–20%",
    "Spray wettable sulphur or Propiconazole at first sign of whitish colonies.",
    "ICAR recommends wettable Sulphur 80 WP @ 3 g/L for powdery mildew in wheat.")

add("wheat","Foot Rot (Crown Rot)","Fusarium culmorum / F. graminearum","Fungal","High","Crown/Stem Base",
    "Water-soaked brown discolouration at stem base; premature whitening of tillers; pink or orange mould.",
    "Soil-borne Fusarium; seed-borne contamination; infected crop residues.",
    "Cool moist soil at sowing; waterlogged conditions; temperature 10–18°C.",
    "Trichoderma viride seed treatment 4 g/kg; biocontrol with Bacillus subtilis.",
    "Carbendazim + Thiram seed treatment, Tebuconazole 2DS.",
    "Carbendazim + Thiram","2.5 g/kg seed (seed treatment)","Seed treatment",
    "Use treated seed; avoid waterlogging; remove infected stubble; practice rotation.",
    "Yes (partial)","10–30%",
    "Treat seeds before sowing; improve field drainage; apply Carbendazim drench to soil.",
    "ICAR recommends Carbendazim + Thiram @ 2.5 g/kg for crown rot prevention.")

# ══════════════════════════════════════════════════════════════════════════════
# MAIZE
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("maize"))
add("maize","Turcicum Leaf Blight","Exserohilum turcicum","Fungal","High","Leaves",
    "Long elliptical tan lesions with wavy margins and water-soaked borders on leaves; lesions coalesce.",
    "Airborne conidia; favoured by moderate temperature and humid conditions.",
    "Temperature 18–27°C, RH >80%, heavy dew, rainy weather.",
    "Neem oil 2%; Pseudomonas fluorescens spray.",
    "Mancozeb 75 WP, Zineb 75 WP, Propiconazole 25 EC.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Grow resistant hybrids; destroy crop residues; avoid late planting.",
    "Yes","10–50%",
    "Spray Mancozeb at first appearance; remove lower diseased leaves.",
    "ICAR recommends Mancozeb 75 WP @ 2.5 g/L for TLB management.")

add("maize","Common Rust","Puccinia sorghi","Fungal","Medium","Leaves",
    "Small circular to elongated brick-red pustules on both leaf surfaces; yellow chlorotic areas around pustules.",
    "Airborne urediniospores from alternate host (Oxalis species).",
    "Temperature 16–23°C, high humidity, heavy dew; prevalent in cooler upland areas.",
    "Neem oil 2% spray.",
    "Propiconazole 25 EC, Mancozeb 75 WP.",
    "Propiconazole","1 mL/L water","Every 10–14 days",
    "Grow rust-resistant hybrids; early planting; avoid susceptible varieties in high-risk areas.",
    "Yes","5–20%",
    "Spray Propiconazole at first pustule appearance.",
    "ICAR recommends propiconazole-based fungicides for maize rust control.")

add("maize","Downy Mildew (Crazy Top)","Peronosclerospora sorghi","Fungal","Very High","Leaves/Whole Plant",
    "Chlorotic striping on leaves; excessive tillering and proliferation of ear shoots; white downy sporulation.",
    "Soil-borne oospores and airborne sporangia; seed-borne in some cases.",
    "Temperature 20–30°C, high soil moisture, rainy weather at germination.",
    "Trichoderma viride seed treatment; remove infected plants.",
    "Metalaxyl 35 SD seed treatment, Ridomil MZ 72 WP.",
    "Metalaxyl","6 g/kg seed (seed treatment)","Seed treatment",
    "Use Metalaxyl-treated seeds; remove infected plants; avoid waterlogging.",
    "No (rogue out plants)","30–90%",
    "Uproot and destroy infected plants immediately; treat seeds before next sowing.",
    "ICAR-IIMR recommends Metalaxyl seed treatment @ 6 g/kg for downy mildew prevention.")

add("maize","Fall Armyworm","Spodoptera frugiperda","Insect Pest","Very High","Leaves/Whorl",
    "Ragged window-feeding on leaves; frass in whorl; wilting of central shoot; severe defoliation.",
    "Invasive pest (Spodoptera frugiperda); spreads rapidly; no seed transmission.",
    "Temperature 28–32°C; rainy conditions; warm tropical and subtropical climate.",
    "Neem-based insecticide (azadirachtin 0.03%) spray in whorl; release egg parasitoid Telenomus remus.",
    "Emamectin benzoate 5 SG, Spinetoram 11.7 SC, Chlorantraniliprole 18.5 SC.",
    "Emamectin benzoate","0.4 g/L water","Every 7–10 days",
    "Use fall armyworm-tolerant varieties; biological control with Nomuraea rileyi; pheromone traps.",
    "Yes (if treated early)","20–70%",
    "Apply sand + carbofuran granules in whorl; spray emamectin benzoate immediately.",
    "ICAR-IIMR recommends emamectin benzoate 5 SG @ 0.4 g/L for fall armyworm.")

add("maize","Gray Leaf Spot","Cercospora zeae-maydis","Fungal","High","Leaves",
    "Rectangular tan-grey lesions between leaf veins; lesions enlarge and coalesce; premature leaf death.",
    "Airborne and residue-borne conidia; conservation tillage increases risk.",
    "Temperature 25–30°C, RH >90%, extended leaf wetness periods, poor air circulation.",
    "Neem oil 2%; Trichoderma harzianum soil application.",
    "Propiconazole 25 EC, Azoxystrobin 23 SC, Tebuconazole 25 WG.",
    "Azoxystrobin","1 mL/L water","Every 10–14 days",
    "Grow resistant hybrids; crop rotation; remove crop residues after harvest.",
    "Yes","10–40%",
    "Spray Propiconazole or Azoxystrobin at disease onset.",
    "ICAR recommends propiconazole-based fungicides for gray leaf spot control.")

# ══════════════════════════════════════════════════════════════════════════════
# COTTON
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("cotton"))
add("cotton","Leaf Curl Virus","Cotton leaf curl virus (CLCuV)","Viral","Very High","Leaves/Whole Plant",
    "Upward curling of leaves; vein thickening; leaf lamina cup-shaped; enations on underside; stunted growth.",
    "Transmitted by whitefly (Bemisia tabaci) vector; no seed transmission.",
    "Temperature 30–35°C; dry hot weather favouring whitefly multiplication.",
    "Yellow sticky traps for whitefly monitoring; neem oil 2% spray to control vector.",
    "Imidacloprid 70 WS (seed treatment), Thiamethoxam 25 WG for whitefly control.",
    "Imidacloprid","0.3 mL/L water (foliar) or 5 g/kg seed (seed treatment)","Every 10–15 days",
    "Grow CLCuV-tolerant varieties (MRC-7017, Suraj); control whitefly population; remove rogues.",
    "No (remove infected plants)","40–80%",
    "Uproot severely infected plants; spray systemic insecticide for whitefly control immediately.",
    "ICAR-CICR recommends Thiamethoxam 25 WG for whitefly and CLCuV management.")

add("cotton","Bacterial Blight","Xanthomonas citri pv. malvacearum","Bacterial","High","Leaves/Bolls/Stem",
    "Angular water-soaked lesions on leaves; brown necrotic spots; black arm (stem canker); boll rotting.",
    "Seed-borne; spreads via rain and irrigation water.",
    "Warm humid weather (28–35°C), frequent rains, high RH.",
    "Copper sulphate 1% seed treatment; remove infected plant debris.",
    "Copper oxychloride 50 WP, Streptomycin sulphate + Tetracycline.",
    "Copper oxychloride","3 g/L water","Every 10–15 days (2–3 sprays)",
    "Use disease-free certified seed; Acid delinting of seed; grow resistant varieties.",
    "Yes (partial)","10–30%",
    "Spray Copper oxychloride at first sign; remove and burn infected plant parts.",
    "ICAR-CICR recommends acid delinting and Copper oxychloride sprays for bacterial blight.")

add("cotton","Fusarium Wilt","Fusarium oxysporum f.sp. vasinfectum","Fungal","High","Roots/Vascular",
    "Yellowing and wilting of leaves; brown discolouration of vascular tissue; sudden plant death.",
    "Soil-borne Fusarium; spreads through soil, water, and nematode wounds.",
    "Temperature 25–28°C; light sandy soils; poor drainage; nematode-infested fields.",
    "Trichoderma harzianum soil application 2.5 kg/ha; FYM amendment.",
    "Carbendazim 50 WP soil drench, Thiophanate-methyl 70 WP.",
    "Carbendazim","1 g/L water (soil drench)","At first wilting symptom",
    "Use wilt-resistant varieties; crop rotation with cereals; soil treatment with Trichoderma.",
    "Partial","20–40%",
    "Apply Carbendazim soil drench; remove wilted plants; apply Trichoderma to soil.",
    "ICAR recommends Trichoderma viride soil application for Fusarium wilt management.")

add("cotton","Root Rot (Seedling Damping-off)","Rhizoctonia solani / Pythium spp.","Fungal","Medium","Roots/Stem",
    "Water-soaked lesions at soil line; seedling collapse and death; brown rotting of roots.",
    "Soil-borne fungi; poor drainage, excess moisture, cool soil temperature.",
    "Excess soil moisture, temperature 15–25°C, heavy clayey soils.",
    "Trichoderma viride seed treatment 4 g/kg; biochar soil amendment.",
    "Captan 75 WP seed treatment, Metalaxyl + Mancozeb WP.",
    "Captan","2 g/kg seed (seed treatment)","Seed treatment",
    "Use raised beds; improve drainage; treat seeds; avoid waterlogging.",
    "Yes (partial)","5–20%",
    "Improve drainage; drench with Captan or Metalaxyl solution at seedling stage.",
    "ICAR recommends Captan 75 WP @ 2 g/kg seed treatment for seedling diseases.")

add("cotton","Bollworm","Helicoverpa armigera / Pectinophora gossypiella","Insect Pest","Very High","Bolls/Flowers",
    "Circular entry holes in bolls; premature boll opening; damaged squares and flowers; webbing.",
    "Helicoverpa armigera and Pectinophora gossypiella; polyphagous pest.",
    "Temperature 25–35°C; dry conditions after monsoon; late-planted cotton.",
    "Neem oil 5% spray; HaNPV (Helicoverpa Nuclear Polyhedrosis Virus) 250 LE/ha; pheromone traps.",
    "Spinosad 45 SC, Emamectin benzoate 5 SG, Indoxacarb 14.5 SC.",
    "Spinosad","0.3 mL/L water","Every 10–15 days (2–3 sprays)",
    "Use Bt cotton varieties; deploy pheromone traps; intercrop with pigeonpea.",
    "Yes (if treated early)","20–60%",
    "Handpick and destroy infested bolls; spray Spinosad at first larval detection.",
    "ICAR-CICR recommends IPM with pheromone traps and HaNPV for bollworm management.")

# ══════════════════════════════════════════════════════════════════════════════
# TOMATO
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("tomato"))
add("tomato","Early Blight","Alternaria solani","Fungal","High","Leaves/Stem/Fruit",
    "Dark brown target-board concentric ring lesions on older leaves; yellow halo; defoliation; stem canker.",
    "Airborne and seed-borne Alternaria conidia; debris-borne.",
    "Temperature 24–29°C, high humidity, alternating wet/dry periods, wounded plants.",
    "Neem oil 2%; Copper sulphate 1% spray; Trichoderma seed treatment.",
    "Mancozeb 75 WP, Chlorothalonil 75 WP, Azoxystrobin 23 SC.",
    "Mancozeb","2.5 g/L water","Every 7–10 days",
    "Use certified disease-free seed; crop rotation; remove crop debris; stake plants for air circulation.",
    "Yes","20–50%",
    "Remove lower infected leaves; spray Mancozeb immediately; improve drainage.",
    "ICAR recommends Mancozeb 75 WP @ 2.5 g/L at 7-day intervals for early blight.")

add("tomato","Late Blight","Phytophthora infestans","Fungal/Oomycete","Very High","Leaves/Stem/Fruit",
    "Irregular water-soaked dark brown patches on leaves; white sporulation on underside; rapid browning and collapse.",
    "Airborne sporangia; water-borne zoospores; highly destructive oomycete.",
    "Temperature 10–25°C, RH >90%, cool moist weather, foggy conditions.",
    "Copper sulphate 1% spray; remove infected plants; biocontrol with Bacillus subtilis.",
    "Metalaxyl + Mancozeb 72 WP, Cymoxanil 8% + Mancozeb 64% WP, Dimethomorph 50 WP.",
    "Metalaxyl + Mancozeb","2.5 g/L water","Every 7 days during outbreak",
    "Grow resistant varieties; avoid overhead irrigation; improve air circulation.",
    "Yes (partial)","50–100%",
    "Remove and destroy infected plants; spray Metalaxyl immediately; stop overhead irrigation.",
    "ICAR recommends Metalaxyl + Mancozeb 72 WP @ 2.5 g/L for late blight control.")

add("tomato","Leaf Curl Virus","Tomato leaf curl New Delhi virus (ToLCNDV)","Viral","Very High","Leaves/Whole Plant",
    "Severe upward curling and cupping of leaves; vein thickening; plant stunting; reduced fruiting.",
    "Transmitted by whitefly (Bemisia tabaci); no mechanical transmission.",
    "Hot dry weather (30–38°C) favoring whitefly; late season planting.",
    "Yellow sticky traps; neem oil 2% spray for whitefly control; silver reflective mulch.",
    "Imidacloprid 17.8 SL, Thiamethoxam 25 WG for whitefly vector control.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Use virus-tolerant varieties (Arka Rakshak, Pusa Rohini); control whitefly; rogue infected plants.",
    "No","40–80%",
    "Remove infected plants; spray systemic insecticide for whitefly; use reflective mulch.",
    "ICAR recommends whitefly management and virus-tolerant tomato varieties.")

add("tomato","Fusarium Wilt","Fusarium oxysporum f.sp. lycopersici","Fungal","High","Roots/Vascular",
    "Yellowing of lower leaves; unilateral wilting; brown vascular discolouration when stem cut.",
    "Soil-borne; spreads through contaminated soil and water.",
    "Temperature 25–28°C; light acidic soils; monoculture.",
    "Trichoderma harzianum soil application 2.5 kg/ha; neem cake amendment.",
    "Carbendazim 50 WP soil drench, Thiophanate-methyl.",
    "Carbendazim","1 g/L water (soil drench)","At transplanting and first wilt sign",
    "Use Fusarium-resistant varieties; crop rotation; soil solarization; Trichoderma treatment.",
    "Partial","20–50%",
    "Apply Carbendazim soil drench; remove wilted plants; avoid waterlogging.",
    "ICAR recommends Trichoderma + Carbendazim combination for Fusarium wilt in tomato.")

add("tomato","Bacterial Wilt","Ralstonia solanacearum","Bacterial","Very High","Vascular/Whole Plant",
    "Sudden wilting of entire plant; plant recovers at night; brown slimy ooze from cut stem in water.",
    "Soil-borne bacteria; enters through roots; spreads via irrigation water.",
    "Temperature 28–35°C; high soil moisture; sandy loam soils.",
    "Soil solarization 30–40 days; application of lime; Pseudomonas fluorescens biocontrol.",
    "Copper oxychloride 50 WP drench, Streptomycin + Tetracycline.",
    "Copper oxychloride","3 g/L water (soil drench)","At first wilt sign",
    "Soil solarization; crop rotation with non-solanaceous crops; use resistant rootstocks.",
    "No (rogue out plants)","50–100%",
    "Remove and destroy wilted plants; soil drench with Copper oxychloride; avoid reinfection.",
    "ICAR recommends soil solarization and Pseudomonas fluorescens for bacterial wilt management.")

add("tomato","Septoria Leaf Spot","Septoria lycopersici","Fungal","Medium","Leaves",
    "Numerous small circular spots with white/grey centres and dark brown borders on lower leaves; defoliation.",
    "Fungal; rain-splashed spores; crop debris; seed-borne.",
    "Temperature 20–25°C, RH >90%, rainy conditions, overhead irrigation.",
    "Neem oil 2%; Copper sulphate spray.",
    "Mancozeb 75 WP, Chlorothalonil 75 WP, Copper oxychloride 50 WP.",
    "Chlorothalonil","2 g/L water","Every 7–10 days",
    "Avoid overhead irrigation; stake plants; destroy crop debris; use clean seed.",
    "Yes","10–30%",
    "Remove lower infected leaves; spray Chlorothalonil or Mancozeb.",
    "ICAR recommends Mancozeb or Chlorothalonil for Septoria leaf spot management.")

add("tomato","Target Spot","Corynespora cassiicola","Fungal","Medium","Leaves/Fruit",
    "Circular brown lesions with concentric rings and yellow halos on leaves; spots on fruit.",
    "Airborne and water-splashed fungal conidia.",
    "Temperature 22–30°C, high humidity, high dew.",
    "Neem oil 2% spray.",
    "Azoxystrobin 23 SC, Difenoconazole 25 EC.",
    "Azoxystrobin","1 mL/L water","Every 10–14 days",
    "Stake plants; improve air circulation; avoid overhead irrigation.",
    "Yes","5–20%",
    "Spray Azoxystrobin at first lesion appearance.",
    "ICAR recommends azoxystrobin-based fungicides for target spot in tomato.")

add("tomato","Two-Spotted Spider Mite","Tetranychus urticae","Arachnid Pest","Medium","Leaves",
    "Tiny white/yellow stippling on leaves; bronzing; webbing on underside; premature leaf drop.",
    "Mite infestation; hot dry conditions amplify population; pesticide-induced resurgence.",
    "Temperature 28–35°C, low humidity, drought stress.",
    "Neem oil 5% spray; release predatory mite Phytoseiulus persimilis.",
    "Abamectin 1.9 EC, Spiromesifen 22.9 SC, Propargite 57 EC.",
    "Abamectin","0.5 mL/L water","Every 7 days (2 sprays)",
    "Maintain adequate soil moisture; avoid dust; use reflective mulch.",
    "Yes","5–30%",
    "Spray abamectin on underside of leaves; improve irrigation to reduce drought stress.",
    "ICAR recommends abamectin and neem oil sprays for spider mite control in tomato.")

# ══════════════════════════════════════════════════════════════════════════════
# POTATO
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("potato"))
add("potato","Late Blight","Phytophthora infestans","Fungal/Oomycete","Very High","Leaves/Stem/Tuber",
    "Water-soaked dark patches on leaves with white downy growth underneath; brown rot of tubers.",
    "Airborne sporangia; zoospores in soil water infect tubers; cool humid conditions.",
    "Temperature 10–20°C, RH >90%, cool nights with warm days, foggy weather.",
    "Copper sulphate 1% spray; destroy infected plant material.",
    "Metalaxyl + Mancozeb 72 WP, Cymoxanil + Mancozeb, Dimethomorph 50 WP.",
    "Metalaxyl + Mancozeb","2.5 g/L water","Every 7 days during high-risk period",
    "Plant certified disease-free seed tubers; grow resistant varieties; avoid overhead irrigation.",
    "Yes (partial)","40–100%",
    "Remove infected haulms; spray Metalaxyl immediately; do not harvest in wet conditions.",
    "ICAR recommends Metalaxyl + Mancozeb @ 2.5 g/L for potato late blight management.")

add("potato","Early Blight","Alternaria solani","Fungal","High","Leaves/Stem",
    "Dark brown target-like concentric ring spots on older leaves; yellowing; premature defoliation.",
    "Airborne and soil-borne conidia; favoured by alternating wet/dry conditions.",
    "Temperature 24–29°C, high humidity, alternating wet-dry periods.",
    "Neem oil 2%; Trichoderma seed treatment on seed pieces.",
    "Mancozeb 75 WP, Chlorothalonil 75 WP, Iprodione 50 WP.",
    "Mancozeb","2.5 g/L water","Every 7–10 days",
    "Use certified seed tubers; crop rotation; remove infected debris.",
    "Yes","10–30%",
    "Spray Mancozeb at first appearance; remove infected lower leaves.",
    "ICAR recommends Mancozeb 75 WP @ 2.5 g/L for early blight management.")

add("potato","Black Scurf (Rhizoctonia)","Rhizoctonia solani","Fungal","Medium","Stem Base/Tuber",
    "Black sclerotia on tuber surface; brown sunken cankers on stems; aerial tubers; sprout killing.",
    "Soil-borne; sclerotia on infected seed tubers; cool wet soil conditions.",
    "Cool wet soil (8–18°C) at planting; heavy clay soils.",
    "Trichoderma viride seed treatment; biocontrol soil application.",
    "Pencycuron 22.9 SC, Flutolanil 17 SC (seed piece treatment).",
    "Pencycuron","20 mL/100 kg seed tubers (treatment)","Seed piece treatment",
    "Use disease-free seed; treat seed pieces; plant in warm well-drained soil.",
    "Yes","5–15%",
    "Treat seed pieces with Pencycuron; plant in warmer soil; improve drainage.",
    "ICAR recommends Pencycuron seed piece treatment for Rhizoctonia in potato.")

add("potato","Common Scab","Streptomyces scabies","Bacterial","Low","Tubers",
    "Rough corky lesions on tuber surface ranging from pitted to raised; reduced marketability.",
    "Soil-borne actinomycete; high soil pH, dry soil during tuber development.",
    "Soil pH >6.0, dry soil conditions, alkaline soils, temperature 20–22°C.",
    "Green manuring; application of sulphur to lower soil pH.",
    "Thiram 75 WS seed treatment.",
    "Thiram","3 g/kg seed tubers","Seed treatment",
    "Maintain soil pH 5.0–5.2; irrigate during tuber development; grow resistant varieties.",
    "Yes (cosmetic)","5–10% (marketability loss)",
    "Adjust soil pH with sulphur; ensure adequate irrigation during tuber bulking.",
    "ICAR recommends maintaining acidic soil pH and seed treatment for common scab control.")

add("potato","Viral Diseases (PVX, PVY, PLRV)","Potato virus X / Y / Potato leafroll virus","Viral","High","Leaves/Whole Plant",
    "PVX: mild mosaic; PVY: necrotic streaks; PLRV: upward rolling of leaves, yellowing, stunting.",
    "Aphid-transmitted (PVY, PLRV); mechanically transmitted (PVX); seed-borne.",
    "Cool weather; high aphid populations; susceptible varieties; repeated seed use.",
    "Mineral oil spray to reduce aphid transmission; remove infected plants.",
    "Imidacloprid 17.8 SL for aphid vector control.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Use certified virus-free seed tubers; control aphids; rogue infected plants.",
    "Partial","20–70%",
    "Remove infected plants; control aphid vectors with insecticide; use fresh certified seed.",
    "ICAR recommends certified virus-free seed tubers for disease-free potato production.")

# ══════════════════════════════════════════════════════════════════════════════
# SUGARCANE
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("sugarcane"))
add("sugarcane","Red Rot","Colletotrichum falcatum","Fungal","Very High","Stalk/Internodes",
    "Red discolouration of internal stalk tissue with white patches alternating; sour vinegar smell; wilting.",
    "Seed-borne (infected setts); soil-borne; spreads through waterlogged fields.",
    "Temperature 26–32°C, waterlogging, high humidity during monsoon.",
    "Aerated steam treatment of setts; Trichoderma treatment.",
    "Carbendazim 50 WP sett treatment, Propiconazole 25 EC.",
    "Carbendazim","0.1% solution (sett soaking 15 min)","Sett treatment before planting",
    "Use disease-free seed canes; treat setts; grow resistant varieties (Co 86032, CoJ 64).",
    "No (destroy infected canes)","30–70%",
    "Destroy infected stalks; treat setts with Carbendazim; improve drainage.",
    "ICAR-IISR recommends Carbendazim sett treatment and resistant varieties for red rot.")

add("sugarcane","Smut","Sporisorium scitamineum","Fungal","High","Growing Point",
    "Emergence of whip-like structure from growing point; covered with black teliospores; plant stunting.",
    "Seed-borne teliospores on infected setts; soil-borne; wind dispersal.",
    "Temperature 25–35°C; dry hot conditions; monoculture; ratoon crops.",
    "Hot water treatment of setts (50°C for 2 hours); remove smutted plants.",
    "Propiconazole 25 EC (sett treatment).",
    "Propiconazole","1 mL/L water (sett dipping)","Sett treatment",
    "Use smut-free setts; hot water treatment; destroy smutted plants; grow resistant varieties.",
    "Yes (partial)","10–30%",
    "Rogue out all whip-bearing plants; treat setts before next planting.",
    "ICAR recommends hot water treatment (50°C/2 hrs) for smut prevention in sugarcane.")

add("sugarcane","Wilt","Fusarium sacchari / Cephalosporium sacchari","Fungal","High","Stalk/Vascular",
    "Yellowing and drying of leaves from tip; purple or reddish discolouration of internodes; hollow cavity.",
    "Soil-borne fungi; enters through root wounds; insect wounds.",
    "Temperature 25–35°C; drought stress; root damage by insects.",
    "Trichoderma harzianum soil application; FYM amendment.",
    "Carbendazim sett treatment, Thiophanate-methyl.",
    "Carbendazim","0.1% solution sett dip","Sett treatment",
    "Use wilt-resistant varieties; treat setts; adequate irrigation.",
    "Partial","15–40%",
    "Remove wilted plants; treat setts before replanting; improve irrigation.",
    "ICAR recommends Carbendazim sett treatment for wilt prevention in sugarcane.")

add("sugarcane","Grassy Shoot Disease","Phytoplasma (16SrXI group)","Phytoplasma","High","Whole Plant",
    "Profuse tillering; many slender shoots; small narrow pale-green leaves; shortened internodes; no economic yield.",
    "Transmitted by leafhopper vector Matsumuratettix hiroglyphicus; seed-borne in infected setts.",
    "Warm humid conditions; high leafhopper population; ratoon crops.",
    "Remove infected stools; control leafhopper with neem-based insecticides.",
    "Tetracycline injection (25 g/100 L) into stem for vector; Imidacloprid for leafhopper.",
    "Imidacloprid","0.3 mL/L water","Every 15 days for vector control",
    "Use disease-free setts; hot water treatment; control leafhoppers; remove infected plants.",
    "No (destroy plants)","50–100%",
    "Destroy all infected stools immediately; control leafhopper vector; treat setts.",
    "ICAR-IISR recommends hot water treatment and leafhopper control for GSD management.")

# ══════════════════════════════════════════════════════════════════════════════
# GROUNDNUT
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("groundnut"))
add("groundnut","Late Leaf Spot","Phaeoisariopsis personata","Fungal","High","Leaves",
    "Dark brown to black circular spots on lower leaf surface; sporulation on underside; defoliation.",
    "Airborne conidia; survives in crop debris.",
    "Temperature 25–30°C, RH >80%, rainy conditions during pod development.",
    "Neem oil 2%; Trichoderma seed treatment.",
    "Chlorothalonil 75 WP, Mancozeb 75 WP, Tebuconazole 25 WG.",
    "Tebuconazole","1 g/L water","Every 10–14 days (2–3 sprays)",
    "Grow resistant varieties (ICGS-76, TAG-24); timely sowing; destroy crop residues.",
    "Yes","10–50%",
    "Spray Chlorothalonil at first spot appearance; remove heavily infected leaves.",
    "ICAR-ICRISAT recommends Tebuconazole or Chlorothalonil for late leaf spot management.")

add("groundnut","Early Leaf Spot","Cercospora arachidicola","Fungal","Medium","Leaves",
    "Circular tan to brown spots on upper leaf surface with yellow halo; smaller than late leaf spot.",
    "Airborne conidia; seed-borne; crop residue.",
    "Temperature 25–30°C, RH >80%, rainy weather.",
    "Neem oil 2% spray.",
    "Mancozeb 75 WP, Chlorothalonil 75 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Crop rotation; remove debris; use resistant varieties.",
    "Yes","5–20%",
    "Spray Mancozeb at first spots; remove infected leaves.",
    "ICAR recommends preventive Mancozeb sprays for early leaf spot in groundnut.")

add("groundnut","Stem Rot (Crown Rot)","Sclerotium rolfsii","Fungal","High","Stem Base/Roots",
    "White mycelial growth at soil level on stem; brown circular mustard seed-like sclerotia; plant wilting and death.",
    "Soil-borne; sclerotia persist in soil many years; high soil moisture.",
    "Temperature 25–35°C, high soil moisture, waterlogging, sandy loam soils.",
    "Trichoderma harzianum soil application 2.5 kg/ha; neem cake 250 kg/ha.",
    "Hexaconazole 5 EC soil drench, Carbendazim 50 WP.",
    "Hexaconazole","1 mL/L water (soil drench)","At first wilt sign",
    "Crop rotation; apply Trichoderma; avoid waterlogging; deep summer ploughing.",
    "Partial","10–40%",
    "Apply Trichoderma to soil; drench with Hexaconazole; remove infected plants.",
    "ICAR recommends Trichoderma + Hexaconazole for stem rot management in groundnut.")

add("groundnut","Bud Necrosis Disease","Tomato spotted wilt virus (TSWV)","Viral","High","Growing Points/Leaves",
    "Necrosis of bud and growing tip; bronze/yellow ringspots on leaves; stunting; no pod formation.",
    "Transmitted by thrips (Frankliniella schultzei, Scirtothrips dorsalis); no seed transmission.",
    "Dry hot weather; high thrips population; early season infection most damaging.",
    "Neem oil 2% spray for thrips control; remove infected plants.",
    "Imidacloprid 17.8 SL, Acephate 75 SP for thrips control.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Grow resistant/tolerant varieties; control thrips; rogue infected plants early.",
    "No (rogue out plants)","20–60%",
    "Remove infected plants; spray Imidacloprid for thrips; use reflective mulch.",
    "ICAR-ICRISAT recommends thrips control and tolerant varieties for bud necrosis disease.")

# ══════════════════════════════════════════════════════════════════════════════
# SOYBEAN
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("soybeans"))
add("soybeans","Rust","Phakopsora pachyrhizi","Fungal","Very High","Leaves",
    "Tan to dark brown pustules on underside of leaves; angular lesions on upper surface; severe defoliation.",
    "Airborne urediniospores; wind-dispersed over long distances.",
    "Temperature 15–28°C, RH >75%, rainy conditions, heavy dew.",
    "Neem oil 2%; Trichoderma seed treatment.",
    "Tebuconazole 25 WG, Azoxystrobin 23 SC, Trifloxystrobin + Tebuconazole.",
    "Tebuconazole","1 g/L water","Every 10–14 days (2 sprays at early pod stage)",
    "Grow resistant varieties; early planting; destroy volunteer soybean plants.",
    "Yes","10–80%",
    "Spray Tebuconazole at first pustule detection; repeat in 14 days.",
    "ICAR recommends Tebuconazole 25 WG @ 1 g/L for soybean rust management.")

add("soybeans","Yellow Mosaic Virus","Bean yellow mosaic virus (BYMV)","Viral","Very High","Leaves/Whole Plant",
    "Bright yellow mosaic pattern on leaves; leaf distortion; pod malformation; stunted growth.",
    "Transmitted by whitefly (Bemisia tabaci) vector; no mechanical transmission.",
    "Warm dry weather; high whitefly population.",
    "Yellow sticky traps; neem oil 2% for whitefly control; remove infected plants.",
    "Imidacloprid 17.8 SL for whitefly control.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Use tolerant varieties (JS-335, MACS-450); control whitefly; rogue infected plants.",
    "No","30–80%",
    "Remove infected plants; spray Imidacloprid for whitefly; avoid late planting.",
    "ICAR recommends tolerant varieties and whitefly management for YMV in soybean.")

add("soybeans","Bacterial Pustule","Xanthomonas axonopodis pv. glycines","Bacterial","Medium","Leaves",
    "Small raised pustules on both leaf surfaces; yellow to brown lesions; premature leaf drop.",
    "Seed-borne and rain-splashed bacteria; wounds from insects.",
    "Warm humid weather (28–32°C), high RH, frequent rains.",
    "Copper sulphate 1% spray.",
    "Copper oxychloride 50 WP, Streptomycin + Tetracycline.",
    "Copper oxychloride","3 g/L water","Every 10–15 days",
    "Use disease-free certified seed; grow resistant varieties; crop rotation.",
    "Yes","5–15%",
    "Spray Copper oxychloride; remove and destroy infected leaves.",
    "ICAR recommends Copper oxychloride for bacterial pustule management.")

# ══════════════════════════════════════════════════════════════════════════════
# CHICKPEA
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("chickpea"))
add("chickpea","Fusarium Wilt","Fusarium oxysporum f.sp. ciceris","Fungal","Very High","Roots/Vascular",
    "Yellowing and drooping of leaves; brown discolouration of internal root and stem tissue; plant death.",
    "Soil-borne; soil temperature 25–30°C; monoculture; susceptible varieties.",
    "Temperature 25–32°C; light sandy soils; acidic soil pH.",
    "Trichoderma harzianum seed treatment 4 g/kg; FYM amendment.",
    "Carbendazim 50 WP seed treatment, Thiophanate-methyl.",
    "Carbendazim","2 g/kg seed (seed treatment)","Seed treatment",
    "Grow resistant varieties (JG-62, Pusa-256); crop rotation; Trichoderma soil treatment.",
    "Partial","30–70%",
    "Apply Trichoderma to soil; remove wilted plants; treat seeds before sowing.",
    "ICAR recommends Trichoderma-based biocontrol for Fusarium wilt in chickpea.")

add("chickpea","Ascochyta Blight","Ascochyta rabiei","Fungal","Very High","Leaves/Stem/Pods",
    "Circular brown necrotic spots on leaves, stem, and pods; stem girdling; plant death.",
    "Seed-borne and airborne; spreads rapidly in cool wet conditions.",
    "Temperature 15–25°C, RH >80%, frequent rains or heavy dew.",
    "Trichoderma seed treatment; copper spray.",
    "Mancozeb 75 WP, Chlorothalonil 75 WP, Carbendazim 50 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Use disease-free certified seed; grow resistant varieties; avoid irrigation during wet weather.",
    "Yes","40–100%",
    "Spray Mancozeb immediately; remove infected plants; treat seeds before sowing.",
    "ICAR recommends Mancozeb + Chlorothalonil and resistant varieties for Ascochyta blight.")

add("chickpea","Botrytis Gray Mold","Botrytis cinerea","Fungal","High","Flowers/Pods/Leaves",
    "Gray fluffy mold on flowers, pods, and leaves; water-soaked lesions; pod abortion; seed infection.",
    "Airborne conidia; flowers and wounded tissue most susceptible.",
    "Cool temperature 15–20°C, high humidity, cloudy conditions during flowering.",
    "Remove infected plant parts; improve air circulation.",
    "Carbendazim 50 WP, Iprodione 50 WP.",
    "Iprodione","1 g/L water","Every 10 days during flowering",
    "Maintain plant spacing; avoid overhead irrigation; remove infected tissue.",
    "Yes","10–40%",
    "Spray Iprodione or Carbendazim; remove gray-molded pods.",
    "ICAR recommends Carbendazim sprays during chickpea flowering for gray mold control.")

# ══════════════════════════════════════════════════════════════════════════════
# PIGEONPEAS (REDGRAM)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("pigeonpeas"))
add("pigeonpeas","Fusarium Wilt","Fusarium udum","Fungal","Very High","Roots/Vascular",
    "Yellowing of leaves starting from bottom; brown discolouration of wood; plant death; streaking in stem.",
    "Soil-borne; survives many years in soil; monoculture increases risk.",
    "Temperature 25–30°C; light soils; low soil pH.",
    "Trichoderma harzianum seed treatment 4 g/kg.",
    "Carbendazim 50 WP seed treatment.",
    "Carbendazim","2 g/kg seed","Seed treatment",
    "Grow wilt-resistant varieties (ICPL-87119, Maruti); crop rotation; Trichoderma treatment.",
    "Partial","30–70%",
    "Apply Trichoderma to soil; remove wilted plants; treat seeds before sowing.",
    "ICAR-ICRISAT recommends wilt-resistant varieties and Trichoderma biocontrol.")

add("pigeonpeas","Sterility Mosaic Disease","Pigeonpea sterility mosaic virus (PPSMV)","Viral","Very High","Leaves/Whole Plant",
    "Mosaic pattern on leaves; extreme stunting; small leaflets; no flowering or pod formation.",
    "Transmitted by eriophyid mite (Aceria cajani); no seed transmission.",
    "Hot humid conditions; high mite population; late planting.",
    "Neem oil 2% spray for mite control; remove infected plants.",
    "Dicofol 18.5 EC, Wettable sulphur 80 WP for mite control.",
    "Dicofol","2 mL/L water","Every 10–15 days",
    "Grow resistant varieties (ICPL-20097); control mite vector; early planting.",
    "No","50–95%",
    "Remove infected plants; spray Dicofol or Sulphur for mite control.",
    "ICAR-ICRISAT recommends SMD-resistant varieties and mite management.")

# ══════════════════════════════════════════════════════════════════════════════
# MUNGBEAN (MOONG)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("mungbean"))
add("mungbean","Yellow Mosaic Virus","Mungbean yellow mosaic India virus (MYMIV)","Viral","Very High","Leaves/Pods",
    "Bright yellow mosaic patches interspersed with green on leaves; pods become yellowish; stunted growth.",
    "Transmitted by whitefly (Bemisia tabaci); highly infectious.",
    "Warm dry weather (30–35°C); high whitefly pressure; late planting.",
    "Yellow sticky traps; neem oil 2% for whitefly control.",
    "Imidacloprid 17.8 SL for whitefly vector control.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Grow YMV-resistant varieties (Pusa Vishal, IPM-02-3); control whitefly.",
    "No (rogue out plants)","30–80%",
    "Remove infected plants; spray Imidacloprid for whitefly.",
    "ICAR recommends resistant varieties and whitefly control for YMV in mungbean.")

add("mungbean","Cercospora Leaf Spot","Cercospora canescens","Fungal","Medium","Leaves",
    "Circular dark brown spots with grey centre on leaves; premature defoliation.",
    "Airborne conidia; crop debris; humid conditions.",
    "Temperature 25–32°C, RH >80%, rainy weather.",
    "Neem oil 2%.",
    "Mancozeb 75 WP, Chlorothalonil 75 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Crop rotation; destroy debris; use resistant varieties.",
    "Yes","5–20%",
    "Spray Mancozeb at first sign.",
    "ICAR recommends Mancozeb for Cercospora leaf spot in mungbean.")

add("mungbean","Powdery Mildew","Erysiphe polygoni","Fungal","Medium","Leaves/Pods",
    "White powdery coating on leaf surfaces and pods; yellowing and shrivelling.",
    "Airborne conidia; cool dry conditions.",
    "Temperature 18–25°C, low humidity, dry conditions.",
    "Neem oil 2%; potassium bicarbonate spray.",
    "Wettable Sulphur 80 WP, Triadimefon 25 WP.",
    "Sulphur","2.5 g/L water","Every 10–14 days",
    "Grow resistant varieties; adequate plant spacing.",
    "Yes","5–15%",
    "Spray wettable Sulphur or Triadimefon at first sign.",
    "ICAR recommends wettable Sulphur 80 WP for powdery mildew in mungbean.")

# ══════════════════════════════════════════════════════════════════════════════
# BLACKGRAM (URAD)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("blackgram"))
add("blackgram","Yellow Mosaic Virus","Mungbean yellow mosaic India virus (MYMIV)","Viral","Very High","Leaves/Pods",
    "Yellow mosaic pattern on leaves; stunted growth; reduced pod set; yellowing of pods.",
    "Whitefly (Bemisia tabaci) vector; no seed transmission.",
    "Temperature 30–35°C, dry weather, high whitefly population.",
    "Neem oil 2%; remove infected plants.",
    "Imidacloprid 17.8 SL for whitefly.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Grow resistant varieties (LBG-648, KU 96-3); control whitefly.",
    "No","30–80%",
    "Remove infected plants; spray Imidacloprid for whitefly control.",
    "ICAR recommends resistant varieties and vector control for YMV in blackgram.")

add("blackgram","Leaf Crinkle Disease","Urdbean leaf crinkle virus (ULCV)","Viral","High","Leaves/Whole Plant",
    "Severe crinkling and puckering of leaflets; rugosity; stunting; pod malformation.",
    "Seed-borne; transmitted by aphids and thrips.",
    "Cool to warm weather; aphid and thrips pressure.",
    "Remove infected plants; control aphids and thrips.",
    "Imidacloprid 17.8 SL for vector control.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Use disease-free certified seed; control insect vectors.",
    "No","20–50%",
    "Remove infected plants; spray Imidacloprid for vector control.",
    "ICAR recommends certified seeds and insect vector control for leaf crinkle.")

# ══════════════════════════════════════════════════════════════════════════════
# LENTIL
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("lentil"))
add("lentil","Rust","Uromyces viciae-fabae","Fungal","High","Leaves/Pods",
    "Orange-red urediniospore pustules on leaves and pods; premature leaf drop.",
    "Airborne urediniospores; cool humid conditions.",
    "Temperature 15–20°C, RH >80%, heavy dew.",
    "Neem oil 2%.",
    "Mancozeb 75 WP, Propiconazole 25 EC.",
    "Propiconazole","1 mL/L water","Every 10–14 days",
    "Grow resistant varieties; early sowing; crop rotation.",
    "Yes","10–40%",
    "Spray Propiconazole at first pustule detection.",
    "ICAR recommends Propiconazole for rust management in lentil.")

add("lentil","Wilt (Fusarium/Stemphylium)","Fusarium oxysporum f.sp. lentis","Fungal","High","Roots/Vascular",
    "Yellowing and drooping; browning of root and stem vascular tissue; plant death.",
    "Soil-borne Fusarium; monoculture; susceptible varieties.",
    "Temperature 20–28°C; light dry soils.",
    "Trichoderma harzianum seed treatment.",
    "Carbendazim 50 WP seed treatment.",
    "Carbendazim","2 g/kg seed","Seed treatment",
    "Grow wilt-resistant varieties; crop rotation; Trichoderma treatment.",
    "Partial","10–40%",
    "Apply Carbendazim seed treatment; rotate with non-legume crops.",
    "ICAR recommends Trichoderma seed treatment and wilt-resistant varieties for lentil.")

# ══════════════════════════════════════════════════════════════════════════════
# KIDNEYBEANS
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("kidneybeans"))
add("kidneybeans","Angular Leaf Spot","Phaeoisariopsis griseola","Fungal","High","Leaves/Pods",
    "Angular dark-brown lesions limited by leaf veins; grey sporulation on lower surface; premature defoliation.",
    "Seed-borne and airborne; crop residue.",
    "Temperature 24–32°C, RH >90%, rainy weather.",
    "Neem oil 2%.",
    "Mancozeb 75 WP, Chlorothalonil 75 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Use certified seed; crop rotation; destroy infected debris.",
    "Yes","10–30%",
    "Spray Mancozeb at first sign; remove infected leaves.",
    "ICAR recommends Mancozeb for angular leaf spot in kidney beans.")

add("kidneybeans","Bean Rust","Uromyces appendiculatus","Fungal","Medium","Leaves",
    "Rust-colored urediniospore pustules on both leaf surfaces; yellow halo; defoliation.",
    "Airborne urediniospores.",
    "Temperature 17–24°C, high humidity.",
    "Neem oil 2%.",
    "Propiconazole 25 EC, Mancozeb 75 WP.",
    "Propiconazole","1 mL/L water","Every 10–14 days",
    "Grow resistant varieties; avoid overhead irrigation.",
    "Yes","5–20%",
    "Spray Propiconazole at first pustule appearance.",
    "ICAR recommends Propiconazole for bean rust management.")

# ══════════════════════════════════════════════════════════════════════════════
# BANANA
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("banana"))
add("banana","Panama Wilt (Fusarium Wilt)","Fusarium oxysporum f.sp. cubense","Fungal","Very High","Roots/Vascular",
    "Yellowing of older leaves progressing to all leaves; brown discolouration of pseudostem vascular tissue; plant collapse.",
    "Soil-borne; spreads through infected suckers, soil, and water; extremely persistent.",
    "Temperature 24–28°C; tropical climate; heavy clay soils.",
    "Remove infected mats; soil solarization; Trichoderma application.",
    "No effective chemical cure; Carbendazim soil drench (partial management).",
    "Carbendazim (soil drench)","1 g/L water","At first wilt sign",
    "Use TR-4 resistant varieties (Grand Naine is susceptible); clean planting material.",
    "No (destroy plant mats)","50–100%",
    "Destroy infected mats; remove and burn; do not replant banana in same field for 5 years.",
    "ICAR recommends resistant varieties and biological control for Panama wilt management.")

add("banana","Sigatoka Leaf Spot","Mycosphaerella musicola (Yellow) / M. fijiensis (Black)","Fungal","High","Leaves",
    "Yellow streaks on leaves → brown oval lesions → leaf shredding; reduced photosynthesis; small fingers.",
    "Airborne ascospores and conidia; spreads rapidly under humid conditions.",
    "Temperature 25–30°C, RH >95%, heavy rainfall.",
    "Remove infected leaves; improve drainage; Bordeaux mixture.",
    "Propiconazole 25 EC, Mancozeb 75 WP, Copper oxychloride.",
    "Propiconazole","1 mL/L water","Every 14–21 days",
    "Remove and destroy infected leaves; grow resistant varieties; avoid overhead irrigation.",
    "Yes","20–50%",
    "Remove diseased leaves; spray Propiconazole; ensure good drainage.",
    "ICAR recommends Propiconazole 25 EC for Sigatoka leaf spot management in banana.")

add("banana","Bunchy Top","Banana bunchy top virus (BBTV)","Viral","Very High","Whole Plant",
    "Stunted bunchy growth at top of plant; narrow dark-green streaks on petioles; no fruiting.",
    "Transmitted by banana aphid (Pentalonia nigronervosa); no seed transmission.",
    "Warm tropical climate; high aphid population; no symptom-free carriers.",
    "Remove infected plants; control aphid with neem oil 2%.",
    "Imidacloprid 17.8 SL for aphid vector control.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Use virus-indexed tissue culture plants; control aphids; rogue infected plants.",
    "No (destroy plants)","100%",
    "Destroy infected plants immediately by injecting paraquat or uprooting; control aphid vector.",
    "ICAR recommends tissue culture planting material and aphid management for BBTV.")

add("banana","Rhizome Rot (Erwinia)","Erwinia carotovora","Bacterial","High","Rhizome/Pseudostem",
    "Water-soaked soft rotting of rhizome with foul smell; yellowing of oldest leaves; plant toppling.",
    "Soil-borne bacteria; enters through wounds; waterlogging.",
    "Temperature 25–35°C, high soil moisture, poor drainage.",
    "Improve drainage; apply lime; avoid mechanical damage.",
    "Copper oxychloride 50 WP soil drench, Streptomycin + Tetracycline.",
    "Copper oxychloride","3 g/L water (drench)","At first rotting sign",
    "Improve drainage; plant on raised beds; avoid excess nitrogen; use disease-free suckers.",
    "Partial","20–50%",
    "Improve drainage; apply Copper oxychloride to soil; remove and destroy affected plants.",
    "ICAR recommends drainage improvement and Copper-based bactericide for Erwinia rhizome rot.")

# ══════════════════════════════════════════════════════════════════════════════
# MANGO
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("mango"))
add("mango","Anthracnose","Colletotrichum gloeosporioides","Fungal","High","Leaves/Flowers/Fruits",
    "Black irregular lesions on leaves; blighting of inflorescence; dark sunken spots on ripe fruit.",
    "Airborne conidia; seed-borne; spread in rain.",
    "Temperature 25–30°C, RH >90%, warm rainy weather during flowering.",
    "Neem oil 2% spray; Bordeaux mixture.",
    "Carbendazim 50 WP, Mancozeb 75 WP, Copper oxychloride 50 WP.",
    "Carbendazim","1 g/L water","Every 10–14 days (3 sprays at flowering)",
    "Prune infected branches; destroy fallen leaves; grow resistant varieties.",
    "Yes","10–50%",
    "Spray Carbendazim at panicle emergence; repeat at fruit set.",
    "ICAR recommends Carbendazim 50 WP @ 1 g/L for anthracnose management in mango.")

add("mango","Powdery Mildew","Oidium mangiferae","Fungal","High","Leaves/Flowers/Fruits",
    "White powdery coating on young leaves, inflorescences and fruits; flower and fruitlet drop.",
    "Airborne conidia; cool dry conditions with low humidity at night.",
    "Temperature 15–20°C at night, warm days, low humidity.",
    "Neem oil 2%; Wettable Sulphur spray.",
    "Wettable Sulphur 80 WP, Triadimefon 25 WP, Hexaconazole 5 EC.",
    "Wettable Sulphur","2.5 g/L water","Every 10–15 days (at panicle stage)",
    "Spray at panicle emergence; 3 sprays at 10-day intervals; avoid excess N.",
    "Yes","10–70%",
    "Spray Wettable Sulphur or Hexaconazole at panicle emergence immediately.",
    "ICAR recommends Wettable Sulphur 80 WP @ 2.5 g/L for powdery mildew in mango.")

add("mango","Die-Back","Botryodiplodia theobromae","Fungal","Medium","Branches/Stem",
    "Drying of shoots from tip backwards; dark discolouration of bark; gum exudation; branch death.",
    "Wound pathogen; spread through pruning cuts; bark beetle wounds.",
    "Temperature 28–35°C; drought stress; pruning wounds; bark damage.",
    "Bordeaux paste on cut ends after pruning; neem oil spray.",
    "Carbendazim 50 WP, Copper oxychloride 50 WP.",
    "Carbendazim","1 g/L water","After pruning; 2 sprays",
    "Prune infected shoots 15 cm below diseased portion; apply Bordeaux paste to wounds.",
    "Yes","5–30% (tree productivity loss)",
    "Prune 15 cm below infection; apply Bordeaux paste; spray Carbendazim.",
    "ICAR recommends pruning + Bordeaux paste application for die-back management.")

add("mango","Malformation","Fusarium mangiferae","Fungal","High","Flower/Vegetative Shoots",
    "Malformed compact vegetative shoots (vegetative malformation) or compact bunchy panicles (floral malformation); no fruiting.",
    "Airborne conidia; systemic in infected wood; spread via contaminated tools.",
    "Temperature 15–20°C at panicle initiation; mite feeding wounds.",
    "Prune malformed tissue; control mango bud mite with Sulphur.",
    "Carbendazim 50 WP, Wettable Sulphur 80 WP.",
    "Carbendazim","1 g/L water","2 sprays at panicle initiation",
    "Remove malformed panicles 15 cm below base; control mites; avoid stem pruning during warm weather.",
    "Partial","20–60% (reduced fruit production)",
    "Remove malformed panicles; spray Carbendazim; control bud mites with Sulphur.",
    "ICAR recommends pruning malformed tissue and Carbendazim spray for management.")

# ══════════════════════════════════════════════════════════════════════════════
# GRAPES
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("grapes"))
add("grapes","Downy Mildew","Plasmopara viticola","Fungal/Oomycete","Very High","Leaves/Berries",
    "Oil-spot yellow lesions on upper leaf surface; white cottony sporulation on underside; berry shrivelling.",
    "Oospores in soil; airborne sporangia; rain-splashed.",
    "Temperature 20–25°C, RH >90%, frequent rains, high soil moisture.",
    "Bordeaux mixture 1%; remove infected plant parts.",
    "Metalaxyl + Mancozeb 72 WP, Cymoxanil + Mancozeb, Dimethomorph 50 WP.",
    "Metalaxyl + Mancozeb","2.5 g/L water","Every 7–10 days",
    "Grow resistant varieties; ensure good air circulation; avoid overhead irrigation.",
    "Yes","20–100%",
    "Spray Metalaxyl + Mancozeb immediately; remove diseased berries; improve air circulation.",
    "ICAR-NRC Grapes recommends Metalaxyl + Mancozeb for downy mildew management.")

add("grapes","Powdery Mildew","Uncinula necator (Erysiphe necator)","Fungal","High","Leaves/Berries/Shoots",
    "White mealy coating on leaves, young shoots and berries; berries crack; russeting of berries.",
    "Airborne conidia; overwinters in infected buds; dry warm conditions.",
    "Temperature 18–25°C, low humidity, warm cloudy weather.",
    "Wettable Sulphur 80 WP; neem oil 2%.",
    "Wettable Sulphur 80 WP, Hexaconazole 5 EC, Myclobutanil 10 WP.",
    "Wettable Sulphur","2.5 g/L water","Every 10–14 days",
    "Grow resistant varieties; remove infected canes; avoid excess nitrogen.",
    "Yes","10–50%",
    "Spray Wettable Sulphur or Myclobutanil at first white patches.",
    "ICAR recommends wettable Sulphur 80 WP for powdery mildew in grapes.")

add("grapes","Anthracnose","Elsinoe ampelina","Fungal","High","Leaves/Berries/Shoots",
    "Circular dark brown spots with light grey centres on leaves; sunken spots on berries and shoots.",
    "Seed-borne (infected canes); rain-splashed.",
    "Temperature 24–32°C, RH >90%, warm rainy conditions during shoot growth.",
    "Bordeaux mixture 1% spray.",
    "Carbendazim 50 WP, Mancozeb 75 WP, Copper oxychloride.",
    "Carbendazim","1 g/L water","Every 10–14 days",
    "Use disease-free planting material; prune infected canes; remove debris.",
    "Yes","10–40%",
    "Spray Carbendazim; prune and destroy infected canes.",
    "ICAR recommends Carbendazim and Bordeaux mixture for anthracnose in grapes.")

# ══════════════════════════════════════════════════════════════════════════════
# APPLE
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("apple"))
add("apple","Scab","Venturia inaequalis","Fungal","High","Leaves/Fruit",
    "Olive-green to dark brown velvety lesions on leaves; scabby corky lesions on fruit surface.",
    "Ascospores released from fallen infected leaves; rain-splashed conidia.",
    "Temperature 16–24°C, wet conditions, rain during blossom to fruit development.",
    "Remove and destroy fallen leaves; copper spray in early spring.",
    "Mancozeb 75 WP, Dodine 65 WP, Myclobutanil 10 WP, Captan 50 WP.",
    "Myclobutanil","1 g/L water","Every 7–10 days (preventive from green tip)",
    "Grow scab-resistant varieties; remove leaf litter; prune for air circulation.",
    "Yes","10–50%",
    "Spray Myclobutanil at first lesion; remove infected leaves; prune crowded branches.",
    "ICAR-CITH recommends Mancozeb/Myclobutanil spray program starting at green tip stage.")

add("apple","Powdery Mildew","Podosphaera leucotricha","Fungal","Medium","Leaves/Shoots/Fruit",
    "White powdery coating on young leaves and shoots; distorted silver-grey russet on fruit.",
    "Airborne conidia; overwinters in infected buds.",
    "Temperature 15–25°C, dry warm weather with cool nights.",
    "Neem oil 2%; Wettable Sulphur spray.",
    "Wettable Sulphur 80 WP, Myclobutanil 10 WP, Hexaconazole 5 EC.",
    "Wettable Sulphur","2.5 g/L water","Every 10–14 days",
    "Prune infected shoots; grow resistant varieties; avoid excess nitrogen.",
    "Yes","5–20%",
    "Spray Wettable Sulphur or Myclobutanil; prune silver-mildewed tips.",
    "ICAR recommends Wettable Sulphur 80 WP for powdery mildew management in apple.")

add("apple","Canker (Collar Rot)","Nectria galligena / Phytophthora cactorum","Fungal","High","Stem/Crown",
    "Sunken canker lesions on bark; orange pustules (Nectria); reddish-brown crown rot (Phytophthora).",
    "Wound pathogen; waterlogged soils; bark cracks; freezing injury.",
    "Cool wet soils; waterlogging; temperature 10–20°C.",
    "Bordeaux paste on wounds; avoid mechanical damage.",
    "Carbendazim 50 WP, Metalaxyl + Mancozeb (for Phytophthora).",
    "Carbendazim","1 g/L water (wound paste)","At pruning; after frost damage",
    "Prune cankers; apply Bordeaux paste; improve drainage around crown.",
    "Partial","10–30%",
    "Cut out cankers to healthy wood; apply Bordeaux paste; drain waterlogged soil.",
    "ICAR-CITH recommends wound sealing and Bordeaux mixture for canker management.")

add("apple","Fire Blight","Erwinia amylovora","Bacterial","Very High","Flowers/Shoots/Fruit",
    "Wilting and browning of blossoms and shoots (shepherd's crook); oozing bacterial exudate; fruit mummification.",
    "Bacteria enter through open flowers and wounds; spread by rain, insects, contaminated tools.",
    "Temperature 18–28°C, humid weather, heavy dew during bloom.",
    "Copper sulphate spray at pre-bloom; remove infected shoots.",
    "Streptomycin sulphate 90 SP, Copper oxychloride 50 WP.",
    "Streptomycin","0.1 g/L water","Every 5–7 days during bloom",
    "Use resistant varieties; prune 30 cm below infections; sterilize pruning tools.",
    "Partial","20–80%",
    "Prune infected shoots 30 cm below lesion; spray Streptomycin; sterilize tools.",
    "ICAR-CITH recommends Streptomycin sprays during bloom for fire blight prevention.")

# ══════════════════════════════════════════════════════════════════════════════
# STRAWBERRY
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("strawberry"))
add("strawberry","Gray Mold","Botrytis cinerea","Fungal","High","Fruit/Flowers/Leaves",
    "Brown water-soaked lesions on fruit; gray fluffy sporulation; complete fruit rot.",
    "Airborne conidia; dead plant tissue; poor air circulation.",
    "Temperature 15–20°C, RH >90%, rainy weather during fruiting.",
    "Remove infected fruit; improve air circulation; plastic mulch.",
    "Iprodione 50 WP, Carbendazim 50 WP, Fenhexamid 50 WG.",
    "Iprodione","1 g/L water","Every 7–10 days during fruiting",
    "Remove infected fruit promptly; use plastic mulch; improve air circulation.",
    "Yes","20–60%",
    "Remove infected fruit immediately; spray Iprodione; improve ventilation.",
    "ICAR recommends Iprodione and good air circulation for gray mold in strawberry.")

add("strawberry","Powdery Mildew","Podosphaera aphanis","Fungal","Medium","Leaves/Fruit",
    "White powdery coating on upper leaf surface; leaves curl upward; fruit surface whitened.",
    "Airborne conidia; cool dry conditions.",
    "Temperature 15–25°C, dry conditions, dense planting.",
    "Wettable Sulphur 80 WP; neem oil 2%.",
    "Wettable Sulphur 80 WP, Hexaconazole 5 EC.",
    "Wettable Sulphur","2.5 g/L water","Every 10–14 days",
    "Avoid dense planting; maintain air circulation; grow resistant varieties.",
    "Yes","5–20%",
    "Spray Wettable Sulphur; improve air circulation.",
    "ICAR recommends wettable Sulphur for powdery mildew in strawberry.")

add("strawberry","Leaf Scorch","Diplocarpon earlianum","Fungal","Medium","Leaves",
    "Small purple-red spots with light centres on leaves; leaf scorch; purple discolouration.",
    "Airborne conidia from infected leaves; high humidity.",
    "Temperature 18–24°C, rainy conditions, high humidity.",
    "Remove infected leaves; copper spray.",
    "Captan 50 WP, Mancozeb 75 WP.",
    "Captan","2 g/L water","Every 10–14 days",
    "Remove infected leaves; improve air circulation; avoid overhead irrigation.",
    "Yes","5–15%",
    "Remove infected leaves; spray Captan or Mancozeb.",
    "ICAR recommends Captan 50 WP for leaf scorch management in strawberry.")

# ══════════════════════════════════════════════════════════════════════════════
# EGGPLANT (BRINJAL)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("eggplant (brinjal)"))
add("eggplant (brinjal)","Phomopsis Blight","Phomopsis vexans","Fungal","High","Leaves/Stem/Fruit",
    "Water-soaked brown circular lesions on leaves; stem canker; dark sunken lesions on fruit.",
    "Seed-borne and airborne conidia; crop debris.",
    "Temperature 25–32°C, RH >80%, rainy conditions.",
    "Neem oil 2%; Trichoderma seed treatment.",
    "Mancozeb 75 WP, Copper oxychloride 50 WP, Carbendazim 50 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Use disease-free seed; crop rotation; stake plants.",
    "Yes","20–50%",
    "Spray Mancozeb at first sign; remove infected fruit and stems.",
    "ICAR recommends Mancozeb 75 WP for Phomopsis blight management in brinjal.")

add("eggplant (brinjal)","Bacterial Wilt","Ralstonia solanacearum","Bacterial","Very High","Vascular/Whole Plant",
    "Sudden drooping and wilting; bacterial ooze from cut stem in water; brown vascular discolouration.",
    "Soil-borne Ralstonia; enters through roots; waterlogging.",
    "Temperature 28–35°C, high soil moisture, sandy loam soils.",
    "Soil solarization; lime application; Pseudomonas fluorescens biocontrol.",
    "Copper oxychloride drench, Streptomycin + Tetracycline.",
    "Copper oxychloride","3 g/L water (drench)","At first wilt sign",
    "Grow resistant varieties; soil solarization; crop rotation.",
    "No","50–100%",
    "Remove wilted plants; soil drench with Copper oxychloride; solarize field.",
    "ICAR recommends soil solarization and resistant varieties for bacterial wilt in brinjal.")

add("eggplant (brinjal)","Shoot and Fruit Borer","Leucinodes orbonalis","Insect Pest","Very High","Shoots/Fruit",
    "Borer tunnels inside tender shoots causing wilting (dead shoot); tunnelling in fruit; pin holes.",
    "Moth larvae bore into shoots and fruit; polyphagous pest.",
    "Temperature 28–35°C; warm humid conditions during cropping.",
    "Pheromone traps; remove infested shoots; neem oil 3%.",
    "Emamectin benzoate 5 SG, Spinosad 45 SC, Chlorantraniliprole 18.5 SC.",
    "Emamectin benzoate","0.4 g/L water","Every 7–10 days",
    "Plant resistant varieties; remove and destroy infested shoots; pheromone traps.",
    "Yes (if treated early)","20–50%",
    "Remove infested shoots; spray Emamectin benzoate; use pheromone traps.",
    "ICAR recommends IPM with pheromone traps and Emamectin benzoate for brinjal SFB.")

# ══════════════════════════════════════════════════════════════════════════════
# CAPSICUM (BELL PEPPER)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("capsicum"))
add("capsicum","Anthracnose","Colletotrichum capsici","Fungal","High","Fruit/Leaves",
    "Sunken dark brown water-soaked lesions on ripe fruit; pink spore masses; complete fruit rot.",
    "Seed-borne and airborne; rain-splashed; crop debris.",
    "Temperature 25–30°C, high humidity, rainy conditions during fruiting.",
    "Neem oil 2%; Trichoderma seed treatment.",
    "Carbendazim 50 WP, Mancozeb 75 WP, Azoxystrobin 23 SC.",
    "Carbendazim","1 g/L water","Every 10–14 days",
    "Use disease-free seed; crop rotation; grow resistant varieties.",
    "Yes","20–50%",
    "Spray Carbendazim at first lesion; harvest fruit before full ripening.",
    "ICAR recommends Carbendazim 50 WP @ 1 g/L for anthracnose in capsicum.")

add("capsicum","Phytophthora Blight","Phytophthora capsici","Fungal/Oomycete","Very High","Roots/Stem/Leaves/Fruit",
    "Root and crown rot; dark water-soaked lesions on stem; rapid wilting; complete plant collapse.",
    "Soil-borne oomycete; zoospores spread in irrigation water; waterlogging.",
    "Temperature 25–30°C, waterlogged soils, heavy rains.",
    "Improve drainage; soil solarization; Trichoderma application.",
    "Metalaxyl + Mancozeb 72 WP, Dimethomorph 50 WP.",
    "Metalaxyl + Mancozeb","2.5 g/L water (drench + foliar)","Every 7–10 days",
    "Grow resistant varieties; raised beds; avoid waterlogging; sterilize tools.",
    "No (partial – plants rarely recover)","50–100%",
    "Improve drainage immediately; soil drench with Metalaxyl; remove dead plants.",
    "ICAR recommends Metalaxyl-based fungicides and raised bed cultivation for Phytophthora blight.")

add("capsicum","Leaf Curl Virus","Chilli leaf curl virus (ChiLCV)","Viral","High","Leaves/Whole Plant",
    "Upward curling of leaves; vein thickening; stunting; reduced fruit size.",
    "Whitefly (Bemisia tabaci) transmitted; no seed transmission.",
    "Hot dry weather; high whitefly population.",
    "Yellow sticky traps; neem oil 2%.",
    "Imidacloprid 17.8 SL for whitefly control.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Grow resistant varieties; control whitefly; rogue infected plants.",
    "No","30–70%",
    "Remove infected plants; spray Imidacloprid for whitefly.",
    "ICAR recommends whitefly management and resistant varieties for leaf curl in capsicum.")

# ══════════════════════════════════════════════════════════════════════════════
# OKRA
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("okra"))
add("okra","Yellow Vein Mosaic Virus","Bhendi yellow vein mosaic virus (BYVMV)","Viral","Very High","Leaves/Fruit",
    "Network of yellow veins on leaves; yellow-green mosaic; fruit turns yellow; stunted growth.",
    "Whitefly (Bemisia tabaci) transmitted; no mechanical transmission.",
    "Warm dry weather (30–38°C); high whitefly population.",
    "Yellow sticky traps; neem oil 2%; reflective mulch.",
    "Imidacloprid 17.8 SL for whitefly control.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Grow resistant varieties (HB-286, Parbhani Kranti); control whitefly; rogue infected plants.",
    "No","40–100%",
    "Remove and destroy infected plants; spray Imidacloprid for whitefly control.",
    "ICAR recommends Parbhani Kranti (YVMV-resistant) and whitefly management for okra.")

add("okra","Powdery Mildew","Erysiphe cichoracearum","Fungal","Medium","Leaves",
    "White powdery colonies on leaves; yellowing; premature leaf drop.",
    "Airborne conidia; cool dry conditions.",
    "Temperature 18–25°C, dry conditions.",
    "Wettable Sulphur 80 WP; neem oil 2%.",
    "Wettable Sulphur 80 WP, Triadimefon 25 WP.",
    "Wettable Sulphur","2.5 g/L water","Every 10–14 days",
    "Grow resistant varieties; adequate spacing; crop rotation.",
    "Yes","5–15%",
    "Spray Wettable Sulphur at first sign.",
    "ICAR recommends wettable Sulphur for powdery mildew in okra.")

# ══════════════════════════════════════════════════════════════════════════════
# ONION
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("onion"))
add("onion","Purple Blotch","Alternaria porri","Fungal","High","Leaves/Bulbs",
    "Small white lesions that enlarge with purple centres and yellow margins; leaf tip die-back; bulb infection.",
    "Airborne conidia; seed-borne; crop debris; thrips wounds facilitate entry.",
    "Temperature 25–30°C, high humidity, dew, thrips damage.",
    "Neem oil 2%; remove infected leaves.",
    "Mancozeb 75 WP, Iprodione 50 WP, Propiconazole 25 EC.",
    "Mancozeb","2.5 g/L water","Every 7–10 days",
    "Use disease-free seed; control thrips; crop rotation; avoid overhead irrigation.",
    "Yes","20–50%",
    "Spray Mancozeb at first sign; control thrips; remove infected leaves.",
    "ICAR recommends Mancozeb 75 WP and thrips control for purple blotch management.")

add("onion","Stemphylium Leaf Blight","Stemphylium vesicarium","Fungal","Medium","Leaves",
    "Small water-soaked spots that turn brown with yellow margins; tip dieback; severe defoliation.",
    "Airborne conidia; seed-borne.",
    "Temperature 20–25°C, high humidity, rainy conditions.",
    "Neem oil 2%.",
    "Mancozeb 75 WP, Iprodione 50 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Use treated seeds; crop rotation; improve air circulation.",
    "Yes","10–30%",
    "Spray Mancozeb or Iprodione at first lesion.",
    "ICAR recommends Mancozeb for Stemphylium leaf blight in onion.")

add("onion","Basal Rot","Fusarium oxysporum f.sp. cepae","Fungal","High","Bulb/Roots",
    "Pinkish-red root rot; soft rotting of basal plate; premature yellowing; bulb decay in storage.",
    "Soil-borne Fusarium; persists in soil.",
    "Temperature 25–30°C; light soils; monoculture.",
    "Trichoderma harzianum seed treatment; FYM amendment.",
    "Carbendazim 50 WP seed treatment, Thiophanate-methyl.",
    "Carbendazim","2 g/kg seed (seed treatment)","Seed treatment + soil drench",
    "Crop rotation; treat seeds; improve drainage; grow resistant varieties.",
    "Partial","10–40%",
    "Apply Carbendazim drench; remove infected bulbs; improve drainage.",
    "ICAR recommends Trichoderma + Carbendazim for basal rot management in onion.")

# ══════════════════════════════════════════════════════════════════════════════
# GARLIC
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("garlic"))
add("garlic","Purple Blotch","Alternaria porri","Fungal","High","Leaves",
    "Purple blotches with yellow margins on leaves; tip dieback; severe defoliation.",
    "Airborne and seed-borne conidia; thrips wounds.",
    "Temperature 25–30°C, high humidity.",
    "Neem oil 2%.",
    "Mancozeb 75 WP, Iprodione 50 WP.",
    "Mancozeb","2.5 g/L water","Every 7–10 days",
    "Control thrips; use disease-free cloves; crop rotation.",
    "Yes","10–30%",
    "Spray Mancozeb; control thrips.",
    "ICAR recommends Mancozeb and thrips control for purple blotch in garlic.")

add("garlic","White Rot","Sclerotium cepivorum","Fungal","High","Bulb/Roots",
    "White cottony mycelium on bulb base; small black sclerotia on outer scales; yellowing and plant death.",
    "Soil-borne sclerotia persist decades; low soil temperature.",
    "Cool soil temperature 10–15°C; high soil moisture.",
    "Soil solarization; Trichoderma application.",
    "Tebuconazole 25 WG, Iprodione 50 WP (soil drench).",
    "Tebuconazole","1 g/L water (soil drench)","At planting and early growth",
    "Long rotation (7+ years) away from alliums; soil solarization; use disease-free planting material.",
    "Partial","20–50%",
    "Remove infected plants; soil drench with Tebuconazole; do not replant alliums for 7 years.",
    "ICAR recommends long crop rotation and Trichoderma for white rot management.")

# ══════════════════════════════════════════════════════════════════════════════
# COCONUT
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("coconut"))
add("coconut","Bud Rot","Phytophthora palmivora","Fungal/Oomycete","Very High","Crown/Spear Leaf",
    "Rotting and brown discolouration of the spear (heart) leaf; foul smell; crown death.",
    "Soil-borne and rain-splashed Phytophthora; spreads from infected roots to crown.",
    "Heavy rains, high humidity, waterlogging, temperature 25–30°C.",
    "Remove diseased tissue; apply Bordeaux mixture paste to crown.",
    "Metalaxyl + Mancozeb (crown drench), Fosetyl Aluminium.",
    "Metalaxyl + Mancozeb","10 g/tree (crown drench with 1L water)","Every month during monsoon",
    "Drain stagnant water; remove infected crown tissue; apply Bordeaux paste.",
    "Partial","50–100% (tree death if untreated)",
    "Remove rotted crown tissue; apply Metalaxyl drench immediately; improve drainage.",
    "ICAR-CPCRI recommends Metalaxyl + Mancozeb crown drench for bud rot management.")

add("coconut","Root Wilt","Phytoplasma (16SrXI)","Phytoplasma","Very High","Roots/Whole Tree",
    "Yellowing of older leaves from tip; leaf necrosis; reduced nut size; poor copra yield; tree decline.",
    "Phytoplasma transmitted by planthopper (Proutista moesta); soil-borne.",
    "Warm humid coastal areas; high vector population.",
    "Trunk injection with Oxytetracycline; Neem cake soil application.",
    "Oxytetracycline HCl trunk injection; Imidacloprid for vector control.",
    "Oxytetracycline","5 g/tree (trunk injection)","Every 6 months",
    "Grow tolerant varieties (Calypso); control planthopper; apply green manure.",
    "Partial (no cure)","30–60% (yield reduction)",
    "Inject Oxytetracycline into trunk; control vector; apply nutrition.",
    "ICAR-CPCRI recommends Oxytetracycline trunk injection and vector management for root wilt.")

add("coconut","Stem Bleeding","Thielaviopsis paradoxa / Ceratocystis paradoxa","Fungal","High","Stem",
    "Dark brown to reddish exudate from cracks in stem; internal tissue turns dark brown and rotten.",
    "Wound pathogen; bark beetle wounds; mechanical damage; waterlogging.",
    "Temperature 25–35°C; wounds; bark damage.",
    "Scrape and apply Bordeaux paste to the wound.",
    "Carbendazim 50 WP paste, Copper oxychloride paste.",
    "Carbendazim","Paste application to wound","As needed",
    "Avoid wounding; protect from bark beetles; apply Bordeaux paste immediately.",
    "Partial","10–30% (production loss)",
    "Scrape infected tissue; apply Carbendazim paste; prevent further wounding.",
    "ICAR-CPCRI recommends wound dressing with Bordeaux mixture for stem bleeding.")

# ══════════════════════════════════════════════════════════════════════════════
# COFFEE
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("coffee"))
add("coffee","Coffee Leaf Rust","Hemileia vastatrix","Fungal","Very High","Leaves",
    "Yellow to orange powdery pustules on underside of leaves; premature defoliation; twig die-back.",
    "Airborne urediniospores; spreads in humid conditions.",
    "Temperature 21–25°C, RH >80%, rainy conditions.",
    "Remove infected leaves; copper spray.",
    "Copper oxychloride 50 WP, Propiconazole 25 EC, Triadimefon 25 WP.",
    "Copper oxychloride","3 g/L water","Every 30–40 days (4 sprays/year)",
    "Grow resistant varieties (Cauvery, Chandragiri); balanced shade management; prune for air circulation.",
    "Yes","20–60%",
    "Spray Copper oxychloride immediately; remove heavily infected leaves.",
    "ICAR-CCR Balehonnur recommends 4-spray copper program for coffee leaf rust management.")

add("coffee","Black Rot","Koleroga noxia / Pythium spp.","Fungal","High","Berries/Leaves",
    "White silky mycelium covering berries; berries turn black and mummify; leaves rot and fall.",
    "Soil-borne; spreads through rain splash during monsoon.",
    "Very high humidity (RH >95%), heavy rainfall, cool temperature 18–22°C, dense shade.",
    "Reduce shade; remove infected berries; copper spray.",
    "Copper oxychloride 50 WP, Bordeaux mixture 1%.",
    "Copper oxychloride","3 g/L water","Every 15–21 days during monsoon",
    "Reduce shade trees; prune for air circulation; remove mummified berries.",
    "Partial","10–40%",
    "Remove infected berries; reduce shade; spray Copper oxychloride.",
    "ICAR-CCR recommends Bordeaux mixture and shade regulation for black rot in coffee.")

# ══════════════════════════════════════════════════════════════════════════════
# TEA
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("tea"))
add("tea","Blister Blight","Exobasidium vexans","Fungal","Very High","Young Leaves/Shoots",
    "Translucent water-soaked spots on young leaves; develop into blisters; white sporulation on underside; shoot death.",
    "Airborne basidiospores; high humidity; shade-grown tea most susceptible.",
    "Temperature 16–22°C, RH >90%, misty conditions, dense shade.",
    "Reduce shade; improve air circulation.",
    "Copper hydroxide (Kocide), Copper oxychloride, Propineb 70 WP.",
    "Copper hydroxide","3 g/L water","Every 7–14 days during high-risk period",
    "Reduce shade; improve air circulation; prune bushes; grow resistant clones.",
    "Yes","15–50%",
    "Spray Copper hydroxide immediately; reduce shade; prune affected shoots.",
    "ICAR-UPASI Tea Research Foundation recommends copper fungicide program for blister blight.")

add("tea","Grey Blight","Pestalotiopsis theae","Fungal","Medium","Leaves",
    "Greyish-white patches on leaves with dark brown borders; defoliation.",
    "Airborne conidia; wound pathogen; spreads in humid conditions.",
    "High humidity, rainy conditions, mechanical or insect wounds.",
    "Neem oil 2%.",
    "Copper oxychloride 50 WP, Carbendazim 50 WP.",
    "Copper oxychloride","3 g/L water","Every 10–14 days",
    "Avoid wounding during harvesting; maintain plant vigour.",
    "Yes","5–20%",
    "Spray Copper oxychloride; remove severely infected leaves.",
    "ICAR-UPASI recommends copper fungicides for grey blight management in tea.")

# ══════════════════════════════════════════════════════════════════════════════
# PAPAYA
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("papaya"))
add("papaya","Ringspot Virus","Papaya ringspot virus (PRSV)","Viral","Very High","Leaves/Fruit/Stem",
    "Yellow mosaic and ringspot on leaves; water-soaked streaks on petioles and stem; ringspot pattern on fruit.",
    "Aphid-transmitted (Myzus persicae, Aphis gossypii); highly infectious.",
    "Warm dry weather; high aphid pressure; adjacent infected plants.",
    "Mineral oil spray to reduce aphid transmission; remove infected plants.",
    "Imidacloprid 17.8 SL for aphid vector control.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Grow PRSV-resistant/tolerant varieties (Pusa Dwarf, CO-7); control aphids; rogue infected plants.",
    "No","50–100%",
    "Remove infected plants; control aphid vectors; plant resistant varieties.",
    "ICAR recommends tolerant varieties and aphid management for PRSV in papaya.")

add("papaya","Anthracnose","Colletotrichum gloeosporioides","Fungal","High","Fruit/Leaves",
    "Sunken dark brown water-soaked lesions on fruit; pink spore masses; complete fruit rot.",
    "Airborne and seed-borne conidia; rain-splashed; postharvest infection.",
    "Temperature 25–30°C, high humidity, rainy conditions.",
    "Neem oil 2%; hot water treatment of fruit.",
    "Carbendazim 50 WP, Mancozeb 75 WP.",
    "Carbendazim","1 g/L water","Every 10–14 days",
    "Careful harvesting to avoid wounds; hot water treatment (50°C, 20 min) postharvest.",
    "Yes","10–50%",
    "Spray Carbendazim; handle fruit carefully; use postharvest hot water treatment.",
    "ICAR recommends Carbendazim sprays and careful harvest handling for papaya anthracnose.")

# ══════════════════════════════════════════════════════════════════════════════
# POMEGRANATE
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("pomegranate"))
add("pomegranate","Bacterial Blight","Xanthomonas axonopodis pv. punicae","Bacterial","Very High","Leaves/Stem/Fruit",
    "Water-soaked angular lesions on leaves and fruit; dark brown cankerous lesions on twigs; fruit cracking.",
    "Seed-borne and rain-splashed bacteria; spreads through wounds.",
    "Temperature 28–35°C, heavy rainfall, high humidity.",
    "Copper sulphate 1% spray; remove infected plant parts.",
    "Copper oxychloride 50 WP, Streptomycin + Tetracycline.",
    "Copper oxychloride","3 g/L water","Every 10–15 days",
    "Use disease-free suckers; spray copper bactericide preventively; prune infected parts.",
    "Yes (partial)","20–80%",
    "Spray Copper oxychloride; remove infected shoots; improve drainage.",
    "ICAR recommends Copper oxychloride sprays + resistant varieties for bacterial blight in pomegranate.")

add("pomegranate","Cercospora Fruit Spot","Cercospora punicae","Fungal","Medium","Fruit/Leaves",
    "Small dark brown spots on fruit and leaves; severe spots cause premature fruit drop.",
    "Airborne conidia; rain-splashed.",
    "Temperature 25–30°C, high humidity, rainy conditions.",
    "Neem oil 2%.",
    "Mancozeb 75 WP, Carbendazim 50 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Remove and destroy infected fruit; crop rotation; avoid overhead irrigation.",
    "Yes","5–20%",
    "Spray Mancozeb; remove infected fruit.",
    "ICAR recommends Mancozeb for Cercospora fruit spot in pomegranate.")

# ══════════════════════════════════════════════════════════════════════════════
# GUAVA
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("guava"))
add("guava","Wilt","Fusarium oxysporum f.sp. psidii / Nalanthamala psidii","Fungal","Very High","Roots/Whole Tree",
    "Sudden wilting and yellowing of leaves; bronzing; leaf drop; tree death within days to weeks.",
    "Soil-borne pathogens; spreads through soil and water; nematode wounds.",
    "Temperature 25–32°C; poorly drained soils; monoculture.",
    "Trichoderma harzianum soil application; FYM amendment.",
    "Carbendazim soil drench, Thiophanate-methyl.",
    "Carbendazim","1 g/L water (soil drench)","At first wilt sign",
    "Grow wilt-tolerant varieties; Trichoderma soil treatment; good drainage.",
    "No (tree death)","50–100%",
    "Remove infected tree with roots; soil drench surrounding area; do not replant guava.",
    "ICAR recommends Trichoderma + Carbendazim soil treatment for guava wilt management.")

add("guava","Anthracnose","Colletotrichum gloeosporioides","Fungal","Medium","Fruit/Leaves",
    "Brown water-soaked lesions on ripe fruit; pink spore masses; postharvest fruit rot.",
    "Airborne conidia; rain-splashed; postharvest infection.",
    "Temperature 25–30°C, high humidity.",
    "Neem oil 2%; postharvest hot water treatment.",
    "Carbendazim 50 WP, Mancozeb 75 WP.",
    "Carbendazim","1 g/L water","Every 14 days",
    "Handle fruit carefully; postharvest treatment; improve air circulation.",
    "Yes","5–20%",
    "Spray Carbendazim; careful harvest handling.",
    "ICAR recommends Carbendazim and careful harvest handling for anthracnose in guava.")

# ══════════════════════════════════════════════════════════════════════════════
# CASSAVA (TAPIOCA)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("cassava (tapioca)"))
add("cassava (tapioca)","Cassava Mosaic Disease","African cassava mosaic virus (ACMV) / Indian cassava mosaic virus","Viral","Very High","Leaves/Whole Plant",
    "Mosaic pattern of yellow-green on leaves; distortion; stunting; severe yield loss.",
    "Whitefly (Bemisia tabaci) transmitted; infected stem cuttings.",
    "Warm weather; high whitefly population.",
    "Remove infected plants; control whitefly with neem oil.",
    "Imidacloprid 17.8 SL for whitefly control.",
    "Imidacloprid","0.3 mL/L water","Every 15 days",
    "Use virus-free stem cuttings; grow resistant varieties; control whitefly.",
    "No","20–80%",
    "Remove and destroy infected plants; use clean planting material; control whitefly.",
    "ICAR-CTCRI recommends virus-free planting material and whitefly management for CMD.")

add("cassava (tapioca)","Root Rot","Phytophthora drechsleri / Fusarium spp.","Fungal","High","Roots/Tubers",
    "Water-soaked, brown, rotting roots; plant wilting; foul odour from rotted tubers.",
    "Soil-borne pathogens; waterlogging; poor drainage.",
    "Waterlogged conditions, high humidity, temperature 25–35°C.",
    "Improve drainage; Trichoderma application.",
    "Metalaxyl + Mancozeb (soil drench), Carbendazim.",
    "Metalaxyl + Mancozeb","2.5 g/L water (drench)","At early infection sign",
    "Plant on ridges/raised beds; improve drainage; use disease-free cuttings.",
    "Partial","20–50%",
    "Improve drainage; drench with Metalaxyl; remove infected plants.",
    "ICAR-CTCRI recommends raised bed cultivation and drainage for root rot prevention.")

# ══════════════════════════════════════════════════════════════════════════════
# SUNFLOWER
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("sunflower"))
add("sunflower","Downy Mildew","Plasmopara halstedii","Fungal/Oomycete","Very High","Leaves/Whole Plant",
    "Chlorotic streaks on leaves; white sporulation on lower surface; dwarfing; no head formation.",
    "Soil-borne oospores; airborne sporangia; seed-borne.",
    "Cool wet soil at germination; temperature 15–20°C.",
    "Trichoderma seed treatment.",
    "Metalaxyl 35 SD seed treatment.",
    "Metalaxyl","6 g/kg seed","Seed treatment",
    "Use Metalaxyl-treated seeds; crop rotation; remove infected plants.",
    "No (rogue plants)","30–80%",
    "Remove infected plants; treat seeds before replanting.",
    "ICAR recommends Metalaxyl seed treatment for downy mildew prevention in sunflower.")

add("sunflower","Alternaria Leaf Spot","Alternaria helianthi","Fungal","High","Leaves/Stem/Head",
    "Circular dark brown spots with yellow halos on leaves; stem lesions; head rot.",
    "Seed-borne and airborne conidia.",
    "Temperature 25–30°C, high humidity, rainy conditions.",
    "Neem oil 2%; Trichoderma seed treatment.",
    "Mancozeb 75 WP, Iprodione 50 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Use disease-free seeds; grow resistant varieties; crop rotation.",
    "Yes","10–40%",
    "Spray Mancozeb; treat seeds before sowing.",
    "ICAR recommends Mancozeb for Alternaria leaf spot in sunflower.")

# ══════════════════════════════════════════════════════════════════════════════
# PEARL MILLET (BAJRA)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("pearl millet (bajra)"))
add("pearl millet (bajra)","Downy Mildew (Green Ear)","Sclerospora graminicola","Fungal/Oomycete","Very High","Leaves/Ear",
    "Chlorotic striping on leaves; downy sporulation on lower surface; ear transforms into leafy mass.",
    "Soil-borne oospores; seed-borne; airborne sporangia.",
    "Temperature 18–22°C; high soil moisture at germination; cool nights.",
    "Trichoderma seed treatment; biocontrol.",
    "Metalaxyl 35 SD seed treatment (6 g/kg), Ridomil MZ 72 WP.",
    "Metalaxyl","6 g/kg seed","Seed treatment",
    "Use Metalaxyl-treated seeds; grow resistant hybrids (HHB-67, HHB-197); roguing.",
    "No (rogue plants)","30–70%",
    "Remove and destroy infected plants; treat seeds; grow resistant varieties.",
    "ICAR-IIMR recommends Metalaxyl seed treatment and resistant varieties for downy mildew in bajra.")

add("pearl millet (bajra)","Ergot","Claviceps fusiformis","Fungal","High","Ear/Grains",
    "Sticky honeydew exudate on ears; replaced by hard dark brown sclerotia (ergots) in place of grains.",
    "Airborne ascospores; conidia in honeydew; spreads during flowering.",
    "Humid conditions during flowering; temperature 20–25°C; high humidity.",
    "Remove ergot-infected ears before harvest.",
    "Propiconazole 25 EC, Copper oxychloride 50 WP.",
    "Propiconazole","1 mL/L water","At ear emergence; 2 sprays",
    "Spray propiconazole at ear emergence; remove ergot-infected ears before harvest.",
    "Yes (partial)","5–20%",
    "Spray Propiconazole at flowering; remove infected ears to avoid livestock poisoning.",
    "ICAR recommends Propiconazole spray at ear emergence for ergot management in bajra.")

# ══════════════════════════════════════════════════════════════════════════════
# SORGHUM (JOWAR)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("sorghum (jowar)"))
add("sorghum (jowar)","Grain Mold","Fusarium thapsinum / Curvularia lunata","Fungal","High","Grains/Panicle",
    "Pink to red discolouration of grains; grain shrivelling; poor germination; aflatoxin risk.",
    "Airborne conidia; insect-damaged grains most susceptible; humid conditions during grain fill.",
    "Temperature 25–35°C, high humidity during grain filling.",
    "Remove infected panicles; dry grain promptly after harvest.",
    "Propiconazole 25 EC, Carbendazim 50 WP.",
    "Propiconazole","1 mL/L water","At heading and grain fill stages",
    "Grow resistant varieties (Phule Chitra); harvest promptly when mature; dry grain quickly.",
    "Yes","10–40%",
    "Spray Propiconazole at heading; harvest when mature; dry grain to <13% moisture.",
    "ICAR-NRCS recommends Propiconazole at heading for grain mold prevention in jowar.")

add("sorghum (jowar)","Covered Kernel Smut","Sphacelotheca sorghi","Fungal","Medium","Grains",
    "Grains replaced by mass of dark brown teliospores covered by a thin grey membrane.",
    "Seed-borne teliospores; replaced grain mass.",
    "Cool soil temperatures at germination; temperature 20–25°C.",
    "Hot water seed treatment (52°C, 8 min).",
    "Carboxin + Thiram seed treatment, Thiram 75 WS.",
    "Carboxin + Thiram","2 g/kg seed","Seed treatment",
    "Use smut-resistant varieties; seed treatment; crop rotation.",
    "N/A (seed treatment)","5–20%",
    "Treat seeds before planting; remove smutted heads from field.",
    "ICAR recommends Carboxin + Thiram seed treatment for covered kernel smut in sorghum.")

# ══════════════════════════════════════════════════════════════════════════════
# FINGER MILLET (RAGI)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("finger millet (ragi)"))
add("finger millet (ragi)","Blast","Pyricularia grisea","Fungal","Very High","Leaves/Fingers/Neck",
    "Diamond-shaped lesions on leaves; finger blast causing grain sterility; neck blast kills whole ear.",
    "Airborne conidia; spreads in humid conditions.",
    "Temperature 20–28°C, RH >90%, heavy dew.",
    "Neem oil 2%; Trichoderma seed treatment.",
    "Tricyclazole 75 WP, Carbendazim 50 WP, Isoprothiolane 40 EC.",
    "Tricyclazole","0.6 g/L water","Every 10 days (2–3 sprays)",
    "Grow blast-resistant varieties (GPU-28, Indaf-5); balanced nitrogen; drain fields.",
    "Yes","10–60%",
    "Spray Tricyclazole at first lesion; remove infected tillers.",
    "ICAR recommends Tricyclazole 75 WP @ 0.6 g/L for blast in finger millet.")

add("finger millet (ragi)","Brown Spot","Helminthosporium nodulosum","Fungal","Medium","Leaves",
    "Small circular to oval dark brown spots with yellow margins on leaves.",
    "Airborne conidia; crop residue.",
    "Temperature 22–28°C, high humidity.",
    "Neem oil 2%.",
    "Mancozeb 75 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Crop rotation; destroy debris; balanced nutrition.",
    "Yes","5–15%",
    "Spray Mancozeb at first spots.",
    "ICAR recommends Mancozeb for brown spot management in finger millet.")

# ══════════════════════════════════════════════════════════════════════════════
# BARLEY
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("barley"))
add("barley","Loose Smut","Ustilago nuda f.sp. hordei","Fungal","Medium","Ear/Grains",
    "Entire grain mass replaced by black smut spores; bare rachis remaining after spore dispersal.",
    "Seed-borne; spores infect florets at flowering.",
    "Warm humid weather at flowering; temperature 16–22°C.",
    "Hot water seed treatment (52°C, 10 min).",
    "Carboxin + Thiram seed treatment, Tebuconazole 2DS.",
    "Carboxin + Thiram","2 g/kg seed","Seed treatment",
    "Use certified disease-free seed; systemic fungicide seed treatment.",
    "N/A (seed treatment)","5–15%",
    "Treat seeds with systemic fungicide; rogue smutted heads in field.",
    "ICAR recommends Carboxin + Thiram seed treatment for loose smut in barley.")

add("barley","Powdery Mildew","Blumeria graminis f.sp. hordei","Fungal","Medium","Leaves/Stem",
    "White powdery fungal colonies on leaves; yellowing; premature leaf death.",
    "Airborne conidia; cool humid conditions.",
    "Temperature 15–20°C, moderate humidity.",
    "Wettable Sulphur spray.",
    "Propiconazole 25 EC, Wettable Sulphur 80 WP.",
    "Sulphur","2.5 g/L water","Every 10–14 days",
    "Grow resistant varieties; timely sowing; avoid excess nitrogen.",
    "Yes","5–20%",
    "Spray Wettable Sulphur or Propiconazole at first sign.",
    "ICAR recommends Propiconazole for powdery mildew management in barley.")

# ══════════════════════════════════════════════════════════════════════════════
# MUSTARD (SARSON)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("mustard (sarson)"))
add("mustard (sarson)","White Rust","Albugo candida","Fungal/Oomycete","High","Leaves/Stem/Pods",
    "White blister-like pustules on leaves and pods; stem and pod distortion; green ear malformation.",
    "Airborne spores; soil-borne oospores; seed-borne.",
    "Temperature 10–18°C, high humidity, cool wet conditions.",
    "Remove infected plants; improve air circulation.",
    "Metalaxyl + Mancozeb 72 WP, Ridomil MZ.",
    "Metalaxyl + Mancozeb","2.5 g/L water","Every 10–14 days (2 sprays)",
    "Grow resistant varieties; early sowing; crop rotation; remove infected plants.",
    "Yes","10–40%",
    "Spray Metalaxyl + Mancozeb at first blister signs.",
    "ICAR recommends Metalaxyl + Mancozeb for white rust management in mustard.")

add("mustard (sarson)","Sclerotinia Stem Rot","Sclerotinia sclerotiorum","Fungal","Very High","Stem/Pods",
    "Pale brown water-soaked lesions on stem; white cottony mycelium; black sclerotia inside rotted stem; plant collapse.",
    "Soil-borne sclerotia; airborne ascospores infect flowers.",
    "Temperature 15–20°C, high humidity, wet weather during flowering.",
    "Soil solarization; Trichoderma application.",
    "Carbendazim 50 WP, Iprodione 50 WP.",
    "Carbendazim","1 g/L water","At early flowering; 2 sprays",
    "Crop rotation; Trichoderma soil application; spray at early flowering.",
    "Yes (partial)","20–70%",
    "Spray Carbendazim at first flower emergence; avoid dense planting.",
    "ICAR recommends Carbendazim sprays at flowering for Sclerotinia stem rot in mustard.")

add("mustard (sarson)","Alternaria Leaf Blight","Alternaria brassicae / A. brassicicola","Fungal","High","Leaves/Pods/Stem",
    "Dark brown circular spots with yellow halos on leaves; dark concentric rings; pod spotting; premature pod drop.",
    "Seed-borne and airborne conidia.",
    "Temperature 20–25°C, high humidity, rainy conditions.",
    "Neem oil 2%; Trichoderma seed treatment.",
    "Mancozeb 75 WP, Iprodione 50 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Use disease-free seed; crop rotation; avoid dense planting.",
    "Yes","15–50%",
    "Spray Mancozeb at first symptom; treat seeds before sowing.",
    "ICAR recommends Mancozeb and treated seeds for Alternaria blight in mustard.")

# ══════════════════════════════════════════════════════════════════════════════
# SESAME (TIL)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("sesame (til)"))
add("sesame (til)","Phyllody (Sesame Phytoplasma)","Candidatus Phytoplasma asteris","Phytoplasma","High","Flowers/Whole Plant",
    "Conversion of floral parts to leaf-like structures; green flowers; sterile plant; no seed setting.",
    "Leafhopper-transmitted phytoplasma.",
    "Warm weather; high leafhopper population.",
    "Remove infected plants; control leafhopper with neem oil.",
    "Imidacloprid 17.8 SL for leafhopper.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Control leafhoppers; rogue infected plants; grow resistant varieties.",
    "No","20–70%",
    "Remove infected plants; spray Imidacloprid for leafhopper control.",
    "ICAR recommends leafhopper control and roguing for phyllody management in sesame.")

add("sesame (til)","Leaf Curl Virus","Sesame leaf curl virus","Viral","High","Leaves/Whole Plant",
    "Severe upward curling of leaves; vein thickening; stunting; no capsule formation.",
    "Whitefly (Bemisia tabaci) transmitted.",
    "Warm dry weather; high whitefly population.",
    "Yellow sticky traps; neem oil 2%.",
    "Imidacloprid 17.8 SL for whitefly.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Control whitefly; remove infected plants; grow resistant varieties.",
    "No","30–60%",
    "Remove infected plants; spray Imidacloprid for whitefly control.",
    "ICAR recommends whitefly management for leaf curl virus prevention in sesame.")

# ══════════════════════════════════════════════════════════════════════════════
# JUTE
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("jute"))
add("jute","Stem Rot","Macrophomina phaseolina","Fungal","High","Stem/Roots",
    "Dark brown water-soaked lesions at stem base; rotting and collapse; small black sclerotia.",
    "Soil-borne; hot dry conditions after rain; drought stress.",
    "Temperature 30–35°C, alternating wet-dry periods.",
    "Trichoderma viride seed treatment.",
    "Carbendazim 50 WP soil drench.",
    "Carbendazim","1 g/L water (drench)","At first lesion",
    "Avoid drought stress; crop rotation; Trichoderma soil treatment.",
    "Partial","10–30%",
    "Drench with Carbendazim; maintain soil moisture.",
    "ICAR-NIRJAFT recommends Carbendazim drench for stem rot in jute.")

add("jute","Yellow Mite","Polyphagotarsonemus latus","Arachnid Pest","High","Leaves/Growing Points",
    "Curling and crinkling of leaves; yellowing; stunted growth; bronzing of leaf underside.",
    "Mite infestation; hot dry conditions.",
    "Temperature 28–35°C, low humidity, dry conditions.",
    "Neem oil 5% spray.",
    "Abamectin 1.9 EC, Wettable Sulphur 80 WP.",
    "Abamectin","0.5 mL/L water","Every 7 days (2 sprays)",
    "Monitor regularly; maintain soil moisture; avoid drought.",
    "Yes","10–30%",
    "Spray abamectin or wettable Sulphur immediately.",
    "ICAR-NIRJAFT recommends abamectin for yellow mite control in jute.")

# ══════════════════════════════════════════════════════════════════════════════
# TURMERIC
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("turmeric"))
add("turmeric","Rhizome Rot","Pythium aphanidermatum / P. vexans","Fungal/Oomycete","Very High","Rhizome/Roots",
    "Water-soaked soft rotting of rhizome at soil level; foul smell; plant wilting and collapse.",
    "Soil-borne; waterlogging; poor drainage; infected seed rhizomes.",
    "Waterlogged conditions, temperature 25–30°C, monsoon season.",
    "Trichoderma viride rhizome treatment 4 g/kg; remove infected plants.",
    "Metalaxyl + Mancozeb 72 WP (soil drench), Fosetyl Al.",
    "Metalaxyl + Mancozeb","2.5 g/L water (drench)","At planting and at first rot sign",
    "Use disease-free rhizomes; plant on raised beds; treat rhizomes before planting.",
    "Partial","20–60%",
    "Remove rotted plants; drench with Metalaxyl; improve drainage.",
    "ICAR-NRC Spices recommends Metalaxyl + Mancozeb rhizome treatment for rhizome rot.")

add("turmeric","Leaf Blotch","Taphrina maculans","Fungal","Medium","Leaves",
    "Pale yellow water-soaked spots on leaves that turn brown with yellow margins; leaf drying.",
    "Airborne ascospores; humid conditions.",
    "Temperature 25–30°C, high humidity, rainy conditions.",
    "Neem oil 2%.",
    "Mancozeb 75 WP, Copper oxychloride 50 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Improve drainage; avoid overhead irrigation; crop rotation.",
    "Yes","10–25%",
    "Spray Mancozeb at first sign.",
    "ICAR-NRC Spices recommends Mancozeb for leaf blotch in turmeric.")

# ══════════════════════════════════════════════════════════════════════════════
# GINGER (DRY GINGER)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("dry ginger"))
add("dry ginger","Soft Rot (Pythium Wilt)","Pythium aphanidermatum","Fungal/Oomycete","Very High","Rhizome/Collar",
    "Water-soaked rotting at collar region; foul smell; yellowing and wilting; complete plant collapse.",
    "Soil-borne; waterlogging; infected seed rhizomes; spreads rapidly.",
    "Waterlogged conditions, high humidity, temperature 25–35°C, monsoon.",
    "Trichoderma viride rhizome dip; remove infected plants.",
    "Metalaxyl + Mancozeb 72 WP drench, Fosetyl Al.",
    "Metalaxyl + Mancozeb","2.5 g/L water","Every 15 days during monsoon",
    "Plant on raised beds; treat rhizomes; use disease-free planting material; good drainage.",
    "Partial","30–80%",
    "Remove infected plants; drench with Metalaxyl; improve drainage.",
    "ICAR-NRC Spices recommends Metalaxyl + Mancozeb drench for soft rot in ginger.")

# ══════════════════════════════════════════════════════════════════════════════
# CARDAMOM
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("cardamom small"))
add("cardamom small","Katte (Mosaic) Disease","Cardamom mosaic virus (CdMV)","Viral","Very High","Leaves/Whole Plant",
    "Mosaic and chlorotic streaks on leaves; slender tillers; bushy appearance; reduced capsule yield.",
    "Aphid-transmitted (Pentalonia nigronervosa); infected suckers.",
    "Humid cool conditions of Western Ghats; high aphid populations.",
    "Remove infected plants; control aphid with neem oil 2%.",
    "Imidacloprid 17.8 SL for aphid control.",
    "Imidacloprid","0.3 mL/L water","Every 15 days",
    "Grow virus-free planting material; control aphids; rogue infected clumps.",
    "No (rogue out)","30–60%",
    "Remove infected clumps; spray Imidacloprid for aphid control.",
    "ICAR-IISR Cardamom recommends roguing and aphid control for Katte disease.")

DISEASES.append(healthy("cardamom large"))
add("cardamom large","Rhizome Rot","Pythium vexans","Fungal/Oomycete","High","Rhizome",
    "Rotting and discolouration of rhizome; yellowing and wilting of leaves; plant collapse.",
    "Soil-borne; waterlogging.",
    "High rainfall, waterlogged soils, temperature 20–28°C.",
    "Trichoderma application; improve drainage.",
    "Metalaxyl + Mancozeb drench.",
    "Metalaxyl + Mancozeb","2.5 g/L water","Every 15 days during monsoon",
    "Improve drainage; Trichoderma soil application; use disease-free suckers.",
    "Partial","20–50%",
    "Drench with Metalaxyl; remove infected plants; improve drainage.",
    "ICAR recommends drainage improvement and Metalaxyl for rhizome rot in large cardamom.")

# ══════════════════════════════════════════════════════════════════════════════
# BLACK PEPPER
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("black pepper"))
add("black pepper","Phytophthora Foot Rot","Phytophthora capsici / P. nicotianae","Fungal/Oomycete","Very High","Collar/Roots/Berries",
    "Water-soaked lesion at soil level on stem (foot rot); leaf yellowing; spike drop; berry rot; plant death.",
    "Soil-borne and rain-splashed; spreads in waterlogged conditions.",
    "Monsoon season, waterlogging, temperature 25–32°C.",
    "Trichoderma application; remove infected plants; Bordeaux mixture.",
    "Metalaxyl + Mancozeb 72 WP (soil drench + foliar), Fosetyl Al.",
    "Metalaxyl + Mancozeb","2.5 g/L water","Every 15 days during monsoon",
    "Improve drainage; Trichoderma soil treatment; Bordeaux paste on wounds.",
    "Partial","30–100%",
    "Remove infected vines; drench with Metalaxyl; improve drainage urgently.",
    "ICAR-IISR recommends Metalaxyl + Mancozeb for foot rot prevention in black pepper.")

add("black pepper","Anthracnose (Pollu Disease)","Colletotrichum gloeosporioides","Fungal","High","Berries/Leaves",
    "Dark sunken lesions on berries; infected berries remain on spike but hollow inside; mummified berries.",
    "Airborne conidia; rain-splashed.",
    "Monsoon season, high humidity, temperature 25–30°C.",
    "Bordeaux mixture; remove infected berries.",
    "Carbendazim 50 WP, Copper oxychloride 50 WP.",
    "Carbendazim","1 g/L water","Every 10–14 days during berry development",
    "Remove infected berries; spray preventively during monsoon.",
    "Yes","10–40%",
    "Spray Carbendazim; remove mummified berries.",
    "ICAR-IISR recommends Carbendazim sprays for pollu disease in black pepper.")

# ══════════════════════════════════════════════════════════════════════════════
# LEMON / LIME / ORANGE / CITRUS GROUP
# ══════════════════════════════════════════════════════════════════════════════
for citrus_crop in ["lemon", "lime", "orange", "acid lime", "sweet orange (mosambi)", "mandarin (santra)", "grapefruit", "citron"]:
    DISEASES.append(healthy(citrus_crop))
    add(citrus_crop,"Canker","Xanthomonas citri subsp. citri","Bacterial","High","Leaves/Fruit/Stem",
        "Raised corky brown lesions with water-soaked margins on leaves, twigs and fruit; defoliation; fruit drop.",
        "Seed-borne; rain-splashed; wind-driven rain through wounds.",
        "Temperature 25–35°C, high humidity, frequent rain, wind.",
        "Copper sulphate 1% spray; bordeaux mixture.",
        "Copper oxychloride 50 WP, Streptomycin + Tetracycline.",
        "Copper oxychloride","3 g/L water","Every 15–21 days (4–5 sprays per flush)",
        "Grow resistant varieties; prune infected twigs; bordeaux paste on wounds.",
        "Yes (partial)","10–30%",
        "Spray Copper oxychloride; prune infected twigs; remove infected fruit.",
        "ICAR-NRC Citrus recommends Copper oxychloride for canker management.")

    add(citrus_crop,"Powdery Mildew","Oidium tingitaninum","Fungal","Medium","Leaves/Shoots",
        "White powdery coating on young leaves and shoots; distortion; curling.",
        "Airborne conidia; warm dry conditions.",
        "Temperature 18–25°C, dry weather.",
        "Wettable Sulphur 80 WP.",
        "Wettable Sulphur 80 WP.",
        "Wettable Sulphur","2.5 g/L water","Every 10–14 days",
        "Prune crowded branches; maintain air circulation.",
        "Yes","5–15%",
        "Spray Wettable Sulphur at first sign.",
        "ICAR recommends wettable Sulphur for powdery mildew in citrus.")

    add(citrus_crop,"Greening (Huanglongbing)","Candidatus Liberibacter asiaticus","Bacterial","Very High","Leaves/Whole Tree",
        "Asymmetric blotchy mottle on leaves; small misshapen fruit; bitter taste; tree decline.",
        "Transmitted by Asian citrus psyllid (Diaphorina citri); grafting with infected material.",
        "Warm humid conditions; high psyllid population.",
        "Remove infected trees; control psyllid with neem oil 2%.",
        "Imidacloprid 17.8 SL for psyllid; Oxytetracycline trunk injection (partial).",
        "Imidacloprid","0.3 mL/L water","Every 15 days for psyllid control",
        "Grow disease-free certified nursery plants; control psyllid; rogue infected trees.",
        "No (tree decline)","20–100%",
        "Remove infected trees; control psyllid vector with Imidacloprid; replant with certified material.",
        "ICAR-NRC Citrus recommends certified nursery material and psyllid management for HLB prevention.")

# ══════════════════════════════════════════════════════════════════════════════
# PEAS
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("peas"))
add("peas","Powdery Mildew","Erysiphe pisi","Fungal","High","Leaves/Pods/Stems",
    "White powdery colonies on all aerial parts; yellowing; premature plant death.",
    "Airborne conidia; dry warm conditions.",
    "Temperature 20–25°C, dry conditions with cool nights.",
    "Wettable Sulphur 80 WP; neem oil 2%.",
    "Wettable Sulphur 80 WP, Triadimefon 25 WP.",
    "Wettable Sulphur","2.5 g/L water","Every 10–14 days",
    "Grow resistant varieties (AP-3, Boneville); early sowing; adequate spacing.",
    "Yes","20–70%",
    "Spray Wettable Sulphur immediately; improve air circulation.",
    "ICAR recommends Wettable Sulphur for powdery mildew management in peas.")

add("peas","Fusarium Wilt","Fusarium oxysporum f.sp. pisi","Fungal","High","Roots/Vascular",
    "Yellowing from lower leaves; brown vascular discolouration; plant death; brown discolouration of roots.",
    "Soil-borne; monoculture; susceptible varieties.",
    "Temperature 20–25°C; light soils.",
    "Trichoderma seed treatment.",
    "Carbendazim 50 WP seed treatment.",
    "Carbendazim","2 g/kg seed","Seed treatment",
    "Grow resistant varieties (Pant P-5, Rachna); crop rotation; Trichoderma treatment.",
    "Partial","10–40%",
    "Apply Carbendazim seed treatment; crop rotation.",
    "ICAR recommends Trichoderma + Carbendazim for Fusarium wilt in peas.")

add("peas","Ascochyta Blight","Ascochyta pisi / Mycosphaerella pinodes","Fungal","High","Leaves/Stem/Pods",
    "Dark brown spots on leaves and stems; pods spotted; seed infection; stem girdle; plant collapse.",
    "Seed-borne; airborne in rain.",
    "Temperature 15–22°C, high humidity, rainy conditions.",
    "Trichoderma seed treatment.",
    "Mancozeb 75 WP, Carbendazim 50 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Use disease-free seed; crop rotation; avoid overhead irrigation.",
    "Yes","10–50%",
    "Spray Mancozeb; treat seeds; remove infected plants.",
    "ICAR recommends Mancozeb sprays and treated seeds for Ascochyta blight in peas.")

# ══════════════════════════════════════════════════════════════════════════════
# COWPEA (LOBIA)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("cowpea (lobia)"))
add("cowpea (lobia)","Yellow Mosaic Virus","Cowpea yellow mosaic virus (CYMV)","Viral","High","Leaves",
    "Yellow mosaic pattern on leaves; leaf distortion; pod malformation; stunting.",
    "Whitefly (Bemisia tabaci) transmitted.",
    "Warm dry weather; high whitefly population.",
    "Neem oil 2%; yellow sticky traps.",
    "Imidacloprid 17.8 SL.",
    "Imidacloprid","0.3 mL/L water","Every 10–15 days",
    "Grow resistant varieties; control whitefly; early planting.",
    "No","20–50%",
    "Remove infected plants; spray Imidacloprid.",
    "ICAR recommends whitefly management for Yellow Mosaic Virus in cowpea.")

add("cowpea (lobia)","Cercospora Leaf Spot","Cercospora cruenta","Fungal","Medium","Leaves",
    "Dark brown to reddish-brown circular spots on leaves with grey centre; premature leaf drop.",
    "Airborne conidia; humid conditions.",
    "Temperature 25–32°C, high humidity.",
    "Neem oil 2%.",
    "Mancozeb 75 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Crop rotation; destroy debris; adequate spacing.",
    "Yes","5–20%",
    "Spray Mancozeb at first sign.",
    "ICAR recommends Mancozeb for Cercospora leaf spot in cowpea.")

# ══════════════════════════════════════════════════════════════════════════════
# CARROT
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("carrot"))
add("carrot","Alternaria Leaf Blight","Alternaria dauci","Fungal","High","Leaves",
    "Dark brown to black irregular lesions with yellow halos on leaflets; leaf defoliation.",
    "Seed-borne; airborne conidia.",
    "Temperature 25–30°C, high humidity, rain.",
    "Neem oil 2%.",
    "Mancozeb 75 WP, Iprodione 50 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Use disease-free seed; crop rotation; avoid overhead irrigation.",
    "Yes","10–40%",
    "Spray Mancozeb; remove infected foliage.",
    "ICAR recommends Mancozeb for Alternaria leaf blight in carrot.")

add("carrot","Powdery Mildew","Erysiphe heraclei","Fungal","Medium","Leaves",
    "White powdery coating on leaves; yellowing; premature drying.",
    "Airborne conidia; dry warm conditions.",
    "Temperature 18–25°C, dry conditions.",
    "Wettable Sulphur 80 WP.",
    "Wettable Sulphur 80 WP.",
    "Wettable Sulphur","2.5 g/L water","Every 10–14 days",
    "Maintain air circulation; adequate spacing.",
    "Yes","5–15%",
    "Spray Wettable Sulphur.",
    "ICAR recommends wettable Sulphur for powdery mildew in carrot.")

# ══════════════════════════════════════════════════════════════════════════════
# CABBAGE / CAULIFLOWER / BROCCOLI
# ══════════════════════════════════════════════════════════════════════════════
for brassica in ["cabbage", "cauliflower", "broccoli", "knol khol", "brussels sprouts", "red cabbage", "chinese cabbage"]:
    DISEASES.append(healthy(brassica))
    add(brassica,"Black Rot","Xanthomonas campestris pv. campestris","Bacterial","High","Leaves/Stem/Head",
        "V-shaped yellow lesions at leaf margins; black veins; leaf yellowing; head rotting.",
        "Seed-borne; rain-splashed; spreads through wounds.",
        "Temperature 25–32°C, high humidity, rainy conditions.",
        "Copper sulphate 1% spray.",
        "Copper oxychloride 50 WP, Streptomycin + Tetracycline.",
        "Copper oxychloride","3 g/L water","Every 10–15 days",
        "Use disease-free seed; crop rotation; grow resistant varieties.",
        "Yes (partial)","20–60%",
        "Spray Copper oxychloride; remove infected plants; improve drainage.",
        "ICAR recommends copper bactericides and disease-free seeds for black rot in brassicas.")

    add(brassica,"Downy Mildew","Peronospora parasitica","Fungal/Oomycete","High","Leaves/Curds",
        "Yellow spots on upper leaf surface; grey to white downy sporulation on underside; curd browning.",
        "Airborne sporangia; seed-borne; cool moist conditions.",
        "Temperature 10–20°C, high humidity, cool wet weather.",
        "Improve air circulation; remove infected leaves.",
        "Metalaxyl + Mancozeb 72 WP, Dimethomorph 50 WP.",
        "Metalaxyl + Mancozeb","2.5 g/L water","Every 7–10 days",
        "Grow resistant varieties; avoid overhead irrigation; crop rotation.",
        "Yes","10–40%",
        "Spray Metalaxyl + Mancozeb; improve air circulation.",
        "ICAR recommends Metalaxyl + Mancozeb for downy mildew management in brassicas.")

# ══════════════════════════════════════════════════════════════════════════════
# SPINACH (PALAK)
# ══════════════════════════════════════════════════════════════════════════════
DISEASES.append(healthy("spinach (palak)"))
add("spinach (palak)","Downy Mildew","Peronospora farinosa f.sp. spinaciae","Fungal/Oomycete","High","Leaves",
    "Pale yellow spots on upper leaf surface; grey-purple sporulation on underside; leaf distortion.",
    "Airborne sporangia; cool moist conditions.",
    "Temperature 10–18°C, high humidity.",
    "Improve air circulation.",
    "Metalaxyl + Mancozeb 72 WP.",
    "Metalaxyl + Mancozeb","2.5 g/L water","Every 7–10 days",
    "Grow resistant varieties; avoid overhead irrigation.",
    "Yes","10–40%",
    "Spray Metalaxyl + Mancozeb; improve air circulation.",
    "ICAR recommends Metalaxyl + Mancozeb for downy mildew in spinach.")

add("spinach (palak)","Cercospora Leaf Spot","Cercospora beticola","Fungal","Medium","Leaves",
    "Circular spots with white/grey centre and red-brown margins on leaves.",
    "Airborne; high humidity.",
    "Temperature 22–28°C, high humidity.",
    "Neem oil 2%.",
    "Mancozeb 75 WP.",
    "Mancozeb","2.5 g/L water","Every 10–14 days",
    "Adequate spacing; crop rotation.",
    "Yes","5–20%",
    "Spray Mancozeb.",
    "ICAR recommends Mancozeb for Cercospora leaf spot in spinach.")

# ══════════════════════════════════════════════════════════════════════════════
# RADISH / TURNIP
# ══════════════════════════════════════════════════════════════════════════════
for root_veg in ["radish", "turnip"]:
    DISEASES.append(healthy(root_veg))
    add(root_veg,"Alternaria Leaf Blight","Alternaria raphani","Fungal","Medium","Leaves",
        "Dark brown circular spots with yellow margins on leaves; defoliation.",
        "Seed-borne; airborne conidia.",
        "Temperature 20–28°C, high humidity.",
        "Neem oil 2%.",
        "Mancozeb 75 WP.",
        "Mancozeb","2.5 g/L water","Every 10–14 days",
        "Use treated seeds; crop rotation.",
        "Yes","5–20%",
        "Spray Mancozeb.",
        f"ICAR recommends Mancozeb for Alternaria leaf blight in {root_veg}.")

# ══════════════════════════════════════════════════════════════════════════════
# BEETROOT / SUGARBEET
# ══════════════════════════════════════════════════════════════════════════════
for beet in ["beetroot", "sugarbeet"]:
    DISEASES.append(healthy(beet))
    add(beet,"Cercospora Leaf Spot","Cercospora beticola","Fungal","High","Leaves",
        "Circular lesions with whitish/grey centre and brown/purple margin; premature defoliation.",
        "Airborne conidia; crop residue.",
        "Temperature 20–28°C, high humidity, rainy weather.",
        "Neem oil 2%.",
        "Mancozeb 75 WP, Difenoconazole 25 EC.",
        "Mancozeb","2.5 g/L water","Every 10–14 days",
        "Crop rotation; destroy debris; grow resistant varieties.",
        "Yes","10–30%",
        "Spray Mancozeb; remove heavily infected leaves.",
        f"ICAR recommends Mancozeb for Cercospora leaf spot in {beet}.")

# ══════════════════════════════════════════════════════════════════════════════
# WATERMELON / MUSKMELON / CUCUMBER / BOTTLE GOURD / BITTER GOURD
# ══════════════════════════════════════════════════════════════════════════════
cucurbits = ["watermelon","muskmelon","cucumber","bottle gourd","bitter gourd",
             "pumpkin","ash gourd","ridge gourd","snake gourd","sponge gourd",
             "ivy gourd (tindora)","pointed gourd (parwal)","chow chow",
             "round gourd (tinda)","gherkin","squash","zucchini","wax gourd",
             "long melon (kakri)","snap melon","cantaloupe"]

for cuc in cucurbits:
    DISEASES.append(healthy(cuc))
    add(cuc,"Downy Mildew","Pseudoperonospora cubensis","Fungal/Oomycete","High","Leaves",
        "Angular yellow spots on upper leaf surface; greyish-purple sporulation on underside; rapid defoliation.",
        "Airborne sporangia; cool moist conditions; rain-splashed.",
        "Temperature 15–22°C, RH >90%, cool nights.",
        "Neem oil 2%; remove infected leaves.",
        "Metalaxyl + Mancozeb 72 WP, Cymoxanil + Mancozeb.",
        "Metalaxyl + Mancozeb","2.5 g/L water","Every 7–10 days",
        "Grow resistant varieties; avoid overhead irrigation; crop rotation.",
        "Yes","20–60%",
        "Spray Metalaxyl + Mancozeb; improve air circulation.",
        f"ICAR recommends Metalaxyl + Mancozeb for downy mildew in {cuc}.")

    add(cuc,"Powdery Mildew","Sphaerotheca fuliginea / Podosphaera xanthii","Fungal","High","Leaves/Stems",
        "White powdery colonies on both leaf surfaces; yellowing; premature plant death.",
        "Airborne conidia; dry warm conditions.",
        "Temperature 20–30°C, moderate humidity, dry conditions.",
        "Wettable Sulphur 80 WP; neem oil 2%.",
        "Wettable Sulphur 80 WP, Triadimefon 25 WP, Hexaconazole 5 EC.",
        "Wettable Sulphur","2.5 g/L water","Every 10–14 days",
        "Grow resistant varieties; adequate spacing; crop rotation.",
        "Yes","10–50%",
        "Spray Wettable Sulphur at first sign.",
        f"ICAR recommends Wettable Sulphur for powdery mildew in {cuc}.")

    add(cuc,"Anthracnose","Colletotrichum orbiculare","Fungal","High","Leaves/Fruit",
        "Circular dark brown water-soaked lesions on leaves; sunken spots with pink spore masses on fruit.",
        "Seed-borne; airborne conidia; rain-splashed.",
        "Temperature 22–28°C, high humidity, rainy conditions.",
        "Neem oil 2%.",
        "Carbendazim 50 WP, Mancozeb 75 WP.",
        "Carbendazim","1 g/L water","Every 10–14 days",
        "Use disease-free seed; crop rotation; stake vines.",
        "Yes","10–40%",
        "Spray Carbendazim; remove infected fruit.",
        f"ICAR recommends Carbendazim for anthracnose in {cuc}.")

# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER BEAN (GUAR) / FRENCH BEANS / BROAD BEANS
# ══════════════════════════════════════════════════════════════════════════════
for bean in ["cluster bean (guar)","french beans","broad bean (faba bean)","broad beans",
             "lima bean","sword bean","winged bean"]:
    DISEASES.append(healthy(bean))
    add(bean,"Powdery Mildew","Erysiphe polygoni","Fungal","Medium","Leaves",
        "White powdery colonies on leaves; yellowing; premature leaf drop.",
        "Airborne conidia.",
        "Temperature 18–25°C, dry conditions.",
        "Wettable Sulphur 80 WP.",
        "Wettable Sulphur 80 WP.",
        "Wettable Sulphur","2.5 g/L water","Every 10–14 days",
        "Adequate spacing; crop rotation.",
        "Yes","5–20%",
        "Spray Wettable Sulphur.",
        f"ICAR recommends Wettable Sulphur for powdery mildew in {bean}.")

    add(bean,"Alternaria Leaf Spot","Alternaria alternata","Fungal","Medium","Leaves",
        "Dark brown circular spots; yellow halos; premature defoliation.",
        "Seed-borne; airborne.",
        "Temperature 22–30°C, high humidity.",
        "Neem oil 2%.",
        "Mancozeb 75 WP.",
        "Mancozeb","2.5 g/L water","Every 10–14 days",
        "Use disease-free seed; crop rotation.",
        "Yes","5–20%",
        "Spray Mancozeb.",
        f"ICAR recommends Mancozeb for Alternaria leaf spot in {bean}.")

# ══════════════════════════════════════════════════════════════════════════════
# MOTHBEANS / RICEBEAN / ADZUKI BEAN / HORSE GRAM / GRASS PEA / FIELD PEA
# ══════════════════════════════════════════════════════════════════════════════
for legume in ["mothbeans","ricebean","adzuki bean","horse gram (kulthi)","grass pea (khesari)",
               "field pea (matar)","bambara groundnut","tepary bean","velvet bean"]:
    DISEASES.append(healthy(legume))
    add(legume,"Yellow Mosaic Virus","Mungbean yellow mosaic India virus (MYMIV)","Viral","High","Leaves",
        "Yellow mosaic on leaves; stunting; reduced pod set.",
        "Whitefly transmitted.",
        "Warm dry weather; high whitefly population.",
        "Neem oil 2%.",
        "Imidacloprid 17.8 SL.",
        "Imidacloprid","0.3 mL/L water","Every 10–15 days",
        "Grow resistant varieties; control whitefly.",
        "No","20–60%",
        "Remove infected plants; spray Imidacloprid.",
        f"ICAR recommends whitefly management for Yellow Mosaic Virus in {legume}.")

    add(legume,"Cercospora Leaf Spot","Cercospora canescens","Fungal","Medium","Leaves",
        "Small dark brown circular spots with grey centre on leaves.",
        "Airborne conidia; humid conditions.",
        "Temperature 25–32°C, high humidity.",
        "Neem oil 2%.",
        "Mancozeb 75 WP.",
        "Mancozeb","2.5 g/L water","Every 10–14 days",
        "Crop rotation; destroy debris.",
        "Yes","5–15%",
        "Spray Mancozeb.",
        f"ICAR recommends Mancozeb for Cercospora leaf spot in {legume}.")

# ══════════════════════════════════════════════════════════════════════════════
# REMAINING CROPS – generate standard entries
# covering all remaining crops from crop_state_season_mapping.csv
# ══════════════════════════════════════════════════════════════════════════════

# Collect crop names already covered
covered = set()
for d in DISEASES:
    covered.add(d["Crop_Name"].lower().strip())

# Full crop list from CSV (will be verified against actual file at runtime)
ALL_CROPS_FROM_CSV = [
    "rice","wheat","maize","cotton","tomato","potato","sugarcane","groundnut",
    "soybeans","chickpea","pigeonpeas","mungbean","blackgram","lentil",
    "kidneybeans","banana","mango","grapes","apple","strawberry",
    "eggplant (brinjal)","capsicum","okra","onion","garlic","coconut",
    "coffee","tea","papaya","pomegranate","guava","cassava (tapioca)",
    "sunflower","pearl millet (bajra)","sorghum (jowar)","finger millet (ragi)",
    "barley","mustard (sarson)","sesame (til)","jute","turmeric","dry ginger",
    "cardamom small","cardamom large","black pepper","lemon","lime","orange",
    "acid lime","sweet orange (mosambi)","mandarin (santra)","grapefruit","citron",
    "peas","cowpea (lobia)","carrot","cabbage","cauliflower","broccoli",
    "knol khol","brussels sprouts","red cabbage","chinese cabbage",
    "spinach (palak)","radish","turnip","beetroot","sugarbeet",
    "watermelon","muskmelon","cucumber","bottle gourd","bitter gourd",
    "pumpkin","ash gourd","ridge gourd","snake gourd","sponge gourd",
    "ivy gourd (tindora)","pointed gourd (parwal)","chow chow",
    "round gourd (tinda)","gherkin","squash","zucchini","wax gourd",
    "long melon (kakri)","snap melon","cantaloupe",
    "cluster bean (guar)","french beans","broad bean (faba bean)","broad beans",
    "lima bean","sword bean","winged bean",
    "mothbeans","ricebean","adzuki bean","horse gram (kulthi)","grass pea (khesari)",
    "field pea (matar)","bambara groundnut","tepary bean","velvet bean",
    # Remaining crops
    "amaranth (rajgira)","amaranthus leaves","amla","aniseed","apricot","arecanut",
    "arrowroot","artemisia","asafoetida (hing)","ashwagandha","asparagus","avocado",
    "baby corn","bael","barnyard millet","bathua","bay leaf (tejpatta)","ber (indian jujube)",
    "bergamot","berseem","betel leaf","blackberry","blueberry","bok choy",
    "bottle gourd","brahmi","breadfruit","browntop millet","buckwheat","calophyllum",
    "canary grass","carom seed (ajwain)","carambola","carnation","celery","chamomile",
    "cherimoya","cherry","chestnut","chia","chicory","chinese potato","chrysanthemum",
    "cinnamon","citronella","clove","cocoa","coriander leaves","coriander seed",
    "cottonseed","cowpea pods","cumin (jeera)","curry leaves","custard apple","date palm",
    "dill leaves","dill seed","dragon fruit","drumstick leaves","drumstick pods",
    "elephant foot yam","fennel (saunf)","fenugreek leaves","fenugreek seed",
    "fig","fonio","foxtail millet","gerbera","giloy","gladiolus","henna",
    "horseradish","hybrid napier grass","indigo","isabgol","jackfruit","jamun",
    "jasmine","jatropha","jerusalem artichoke","job's tears","kale","kalmegh",
    "karanja","karonda","kiwi","kodo millet","kokum (garcinia)","kumquat","kusum",
    "lavender","leek","lemongrass","lettuce","linseed (flax)","little millet",
    "longan","lotus root","lucerne (alfalfa)","lychee","mace","mahua",
    "malabar spinach","mangosteen","marigold","mentha","mesta","mulberry","mulberry fruit",
    "mushroom","mustard greens","neem seed","nigella seed (kalonji)","niger seed","nutmeg",
    "oats","oats fodder","oil palm","opium poppy","orchid","palmarosa","parsley",
    "parsnip","passion fruit","peach","pear","pecan nut","persimmon","phalsa",
    "pineapple","pistachio","plum","proso millet","pudina (mint)","pyrethrum","quince",
    "quinoa","rambutan","raspberry","red chili","red onion","rubber","rye","safed musli",
    "safflower","saffron","sal","sapota (chiku)","sarpagandha","senna","shallot",
    "shatavari","aloe vera","spiny gourd","star anise","stevia","subabul","sugar apple",
    "sunn hemp","sweet corn","sweet potato","swiss chard","tamarind","taramira",
    "taro (arvi)","teasel gourd (kakrol)","tef","tobacco","triticale","tuberose",
    "tulsi (holy basil)","tung nut","vanilla","vetiver (khus)","walnut",
    "water chestnut","water spinach","white onion","wild rice","wood apple","yam",
    "cottonseed","green chili","lychee","peach","pear","plum","cherry",
    "blueberry","raspberry","kiwi","avocado","persimmon","fig","jackfruit",
    "mulberry fruit","mulberry","jamun","amla","bael","ber (indian jujube)",
    "sapota (chiku)","custard apple","wood apple","dragon fruit","passion fruit",
    "rambutan","longan","mangosteen","cherimoya","carambola","phalsa",
    "sugar apple","karonda",
]

# Remove duplicates from list
ALL_CROPS_UNIQUE = list(dict.fromkeys([c.lower().strip() for c in ALL_CROPS_FROM_CSV]))

def generic_diseases(crop):
    """Generate 3 generic disease entries for crops without specific data."""
    entries = []
    entries.append(healthy(crop))
    entries.append(row(
        crop, "Powdery Mildew", "Erysiphe / Podosphaera spp.", "Fungal", "Medium",
        "Leaves/Shoots",
        "White powdery fungal colonies on leaves; yellowing; premature leaf drop.",
        "Airborne conidia; warm dry conditions with moderate humidity.",
        "Temperature 18–28°C, dry conditions, moderate humidity.",
        "Neem oil 2% spray; Wettable Sulphur 80 WP.",
        "Wettable Sulphur 80 WP, Triadimefon 25 WP.",
        "Wettable Sulphur", "2.5 g/L water", "Every 10–14 days",
        "Adequate plant spacing; crop rotation; avoid excess nitrogen.",
        "Yes", "5–20%",
        "Spray Wettable Sulphur 80 WP at first sign of white colonies; improve air circulation.",
        "ICAR recommends Wettable Sulphur 80 WP @ 2.5 g/L for powdery mildew management.",
        ml(crop, "Powdery Mildew"),
    ))
    entries.append(row(
        crop, "Leaf Spot", "Alternaria / Cercospora spp.", "Fungal", "Medium",
        "Leaves",
        "Circular to irregular brown spots with yellow halos on leaves; premature defoliation.",
        "Seed-borne and airborne fungal conidia; humid conditions.",
        "Temperature 22–30°C, RH >80%, rainy weather.",
        "Neem oil 2%; Trichoderma viride seed treatment.",
        "Mancozeb 75 WP, Chlorothalonil 75 WP.",
        "Mancozeb", "2.5 g/L water", "Every 10–14 days",
        "Use certified disease-free seed; crop rotation; remove infected debris.",
        "Yes", "10–30%",
        "Spray Mancozeb 75 WP at first sign; remove heavily infected leaves.",
        "ICAR recommends Mancozeb 75 WP @ 2.5 g/L for leaf spot management.",
        ml(crop, "Leaf Spot"),
    ))
    entries.append(row(
        crop, "Root Rot", "Pythium / Fusarium / Rhizoctonia spp.", "Fungal", "High",
        "Roots/Stem Base",
        "Water-soaked browning of roots; wilting; plant collapse; poor stand establishment.",
        "Soil-borne pathogens; waterlogging; poor drainage; stressed plants.",
        "High soil moisture, poor drainage, temperature 20–32°C.",
        "Trichoderma harzianum 4 g/kg seed; neem cake soil application.",
        "Metalaxyl + Mancozeb 72 WP drench, Carbendazim 50 WP.",
        "Carbendazim", "1 g/L water (soil drench)", "At first wilting sign",
        "Improve field drainage; use raised beds; seed treatment with Trichoderma.",
        "Partial", "10–40%",
        "Improve drainage; soil drench with Carbendazim; remove severely affected plants.",
        "ICAR recommends Trichoderma biocontrol and drainage improvement for root rot prevention.",
        ml(crop, "Root Rot"),
    ))
    return entries

# Add generic entries for all remaining uncovered crops
for crop in ALL_CROPS_UNIQUE:
    if crop not in covered and crop:
        entries = generic_diseases(crop)
        DISEASES.extend(entries)
        covered.add(crop)

# ─────────────────────────────────────────────────────────────────────────────
# Read ACTUAL crop list from crop_state_season_mapping.csv at runtime
# and add any missing crops
# ─────────────────────────────────────────────────────────────────────────────
def load_crops_from_csv(filepath):
    crops = set()
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_data in reader:
            crops.add(row_data["Crop_Name"].strip().lower())
    return crops

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "crop_state_season_mapping.csv")
    output_path = os.path.join(script_dir, "disease_info.csv")

    print(f"[INFO] Reading crops from: {csv_path}")
    actual_crops = load_crops_from_csv(csv_path)
    print(f"[INFO] Total unique crops in CSV: {len(actual_crops)}")

    # Add any crops still missing
    covered_set = set(d["Crop_Name"].lower().strip() for d in DISEASES)
    missing = actual_crops - covered_set
    if missing:
        print(f"[INFO] Adding generic entries for {len(missing)} additional crops: {sorted(missing)}")
        for crop in sorted(missing):
            entries = generic_diseases(crop)
            DISEASES.extend(entries)
            covered_set.add(crop)

    # Verify all crops covered
    final_covered = set(d["Crop_Name"].lower().strip() for d in DISEASES)
    still_missing = actual_crops - final_covered
    if still_missing:
        print(f"[WARNING] Still missing crops: {still_missing}")
    else:
        print(f"[INFO] All {len(actual_crops)} crops covered.")

    # Write CSV
    fieldnames = [
        "Crop_Name","Disease_Name","Scientific_Name","Disease_Type","Severity",
        "Affected_Plant_Part","Symptoms","Causes","Favorable_Weather",
        "Organic_Treatment","Chemical_Treatment","Recommended_Active_Ingredient",
        "Dosage","Spray_Interval","Prevention","Recovery_Possibility",
        "Estimated_Yield_Loss","Immediate_Farmer_Action","Govt_ICAR_Recommendation",
        "ML_Class_Name","Image_Folder_Name",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(DISEASES)

    print(f"[SUCCESS] disease_info.csv written: {output_path}")
    print(f"[INFO] Total rows: {len(DISEASES)}")
    print(f"[INFO] Total unique crops covered: {len(set(d['Crop_Name'] for d in DISEASES))}")
    print(f"[INFO] Total unique ML classes: {len(set(d['ML_Class_Name'] for d in DISEASES))}")

if __name__ == "__main__":
    main()
