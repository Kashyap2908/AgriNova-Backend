"""
Explanation Engine — Generates transparent, scientific, and conversational natural-language AI explanations
explaining WHY each fertilizer plan, product, and protection measure was recommended.
"""

import logging

logger = logging.getLogger(__name__)

LEGUMES = ['groundnut', 'peanut', 'soybean', 'chickpea', 'gram', 'moong', 'urad', 'pigeonpea', 'arhar', 'tur', 'pea', 'lentil']
CEREALS = ['wheat', 'rice', 'paddy', 'maize', 'corn', 'jowar', 'sorghum', 'bajra', 'ragi']
COMMERCIAL = ['cotton', 'sugarcane', 'potato', 'onion', 'garlic', 'tomato', 'chilli', 'brinjal', 'banana', 'papaya', 'mango', 'turmeric', 'ginger']


def generate_ai_explanation(crop: str, soil_summary: dict, nutrient_gap: dict,
                             selected_plan: dict, protection_plan: dict,
                             weather_advisory: dict) -> dict:
    """
    Generate clean, structured conversational AI explanation explaining the logic behind the recommendation.
    """
    crop_name = crop.title()
    soil_mode = soil_summary.get('mode', 'ESTIMATED')
    soil_type = soil_summary.get('soil_type', 'Loamy')
    ph_val = soil_summary.get('soil_nutrients', {}).get('pH', 7.0)

    # 1. Soil & Nutrient Diagnosis
    n_def = nutrient_gap.get('N', {}).get('deficit', 0.0)
    p_def = nutrient_gap.get('P', {}).get('deficit', 0.0)
    k_def = nutrient_gap.get('K', {}).get('deficit', 0.0)
    s_def = nutrient_gap.get('S', {}).get('deficit', 0.0)
    zn_def = nutrient_gap.get('Zn', {}).get('deficit', 0.0)

    def_items = []
    if n_def > 2:
        def_items.append(f"Nitrogen deficit of {n_def:.1f} kg/ha")
    if p_def > 2:
        def_items.append(f"Phosphorus deficit of {p_def:.1f} kg/ha")
    if k_def > 2:
        def_items.append(f"Potassium deficit of {k_def:.1f} kg/ha")
    if s_def > 1:
        def_items.append(f"Sulphur deficit of {s_def:.1f} kg/ha")
    if zn_def > 0.2:
        def_items.append(f"Zinc deficit of {zn_def:.1f} kg/ha")

    if def_items:
        diagnosis = (f"Dear Farmer, agronomic diagnostic analysis of your {soil_type} soil for {crop_name} identifies a "
                     f"{', '.join(def_items)}. ")
    else:
        diagnosis = (f"Dear Farmer, your {soil_type} soil demonstrates good overall fertility for {crop_name}. "
                     f"A balanced maintenance nutrition plan has been formulated to optimize yield and sustain long-term soil health. ")

    if soil_mode == 'PRECISION':
        diagnosis += "Calculations were powered by your registered Soil Health Card laboratory test values."
    else:
        diagnosis += f"Soil parameters were scientifically estimated based on {soil_type} ICAR regional baselines and previous cropping history."

    # 2. Fertilizer Plan Rationale & Itemized WHY
    plan_title = selected_plan.get('title', 'Optimized Plan')
    items = selected_plan.get('items', [])

    item_reasons = []
    for item in items:
        fert = item['fertilizer']
        dose = item['dose_kg_ha']
        fname = fert['name']
        cost_kg = fert.get('cost_per_kg', 0.0)
        fn, fp, fk = fert.get('N_pct', 0), fert.get('P_pct', 0), fert.get('K_pct', 0)

        reasons = []
        if fn > 10 and n_def > 0:
            reasons.append(f"supplies {fn}% Nitrogen to satisfy early vegetative canopy requirements at ₹{cost_kg:.2f}/kg N")
        if fp > 10 and p_def > 0:
            reasons.append(f"delivers {fp}% Phosphorus for vigorous root proliferation and early establishment")
        if fk > 10 and k_def > 0:
            reasons.append(f"provides {fk}% Potassium for kernel/grain filling and drought resilience")
        if 'gypsum' in fname.lower():
            reasons.append("supplies 19% Calcium & 16% Sulphur essential for pod formation and oil synthesis")
        if 'rhizobium' in fname.lower() or 'azotobacter' in fname.lower() or 'psb' in fname.lower():
            reasons.append("activates beneficial soil microbes to solubilize bound nutrients")

        if not reasons:
            reasons.append(f"supplies balanced NPK (N:{fn}%, P:{fp}%, K:{fk}%) at economical rates")

        item_reasons.append(f"• **{fname}** ({dose} kg/ha): Selected because it {', '.join(reasons)}.")

    # 3. Crop-Family Agronomic Advisory
    crop_lower = crop_name.lower()
    crop_specific_note = ""

    if any(l in crop_lower for l in LEGUMES):
        crop_specific_note = (
            f"**Agronomic Advisory ({crop_name}):** As a leguminous crop, {crop_name} forms symbiotic root nodules with "
            "Rhizobium bacteria to fix atmospheric Nitrogen. Therefore, synthetic Nitrogen is kept minimal. "
            "Special emphasis is placed on Phosphorus, Sulphur, and Gypsum application during pegging/flowering to prevent empty pods (pops) "
            "and boost oil/protein content."
        )
    elif any(c in crop_lower for c in CEREALS):
        crop_specific_note = (
            f"**Agronomic Advisory ({crop_name}):** {crop_name} is a heavy Nitrogen feeder requiring split applications "
            "(Basal, Active Tillering, and Jointing/Heading). Applying 50% Urea at Basal and splitting the remaining 50% "
            "after irrigation prevents heavy leaching and ammonia volatilization losses."
        )
    else:
        crop_specific_note = (
            f"**Agronomic Advisory ({crop_name}):** High-value commercial crops require a balanced blend of primary NPK, "
            "secondary Calcium/Magnesium, and foliar micronutrient sprays (Zinc/Boron) during square/flower formation to prevent blossom drop."
        )

    plan_rationale = (f"The **{plan_title}** was compiled using multi-objective optimization. "
                      f"Key component rationale:\n" + "\n".join(item_reasons))

    # 4. Soil pH & Soil Amendment Advice
    ph_advice = ""
    if ph_val < 6.0:
        ph_advice = f"Your soil pH is acidic ({ph_val}). Agricultural lime or dolomite incorporation (200 kg/acre) is advised prior to sowing to improve Phosphorus availability."
    elif ph_val > 7.8:
        ph_advice = f"Your soil pH is alkaline ({ph_val}). Gypsum or elemental sulphur incorporation (250 kg/acre) is recommended to reduce alkalinity and unlock fixed micronutrients."
    else:
        ph_advice = f"Soil pH ({ph_val}) is in the optimal range (6.0 - 7.5) for nutrient availability."

    # 5. Protection & Weather Summary
    weather_summary = weather_advisory.get('current_summary', 'Normal field conditions.')
    protection_count = (len(protection_plan.get('weed_management', [])) +
                        len(protection_plan.get('disease_prevention', [])) +
                        len(protection_plan.get('pest_management', [])))

    sections = [diagnosis, plan_rationale]
    if crop_specific_note:
        sections.append(crop_specific_note)
    sections.append(f"**Soil pH Note:** {ph_advice}")
    sections.append(f"**Crop Protection & Weather:** {protection_count} targeted protection guidelines formulated. "
                    f"Real-time weather status ({weather_summary}) has been integrated into application instructions.")

    summary_text = "\n\n".join(sections)

    return {
        'diagnosis_summary': diagnosis,
        'plan_rationale': plan_rationale,
        'ph_advice': ph_advice,
        'crop_specific_note': crop_specific_note,
        'full_explanation': summary_text,
    }
