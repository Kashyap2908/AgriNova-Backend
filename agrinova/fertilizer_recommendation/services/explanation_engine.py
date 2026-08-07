"""
Explanation Engine — Generates transparent, scientific natural-language AI explanations
explaining WHY each fertilizer plan, dosage, and protection measure was recommended.
"""

import logging

logger = logging.getLogger(__name__)


def generate_ai_explanation(crop: str, soil_summary: dict, nutrient_gap: dict,
                             selected_plan: dict, protection_plan: dict,
                             weather_advisory: dict) -> dict:
    """
    Generate clean, structured AI explanation explaining the logic behind the recommendation.
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
    if n_def > 5:
        def_items.append(f"Nitrogen deficit of {n_def} kg/ha")
    if p_def > 5:
        def_items.append(f"Phosphorus deficit of {p_def} kg/ha")
    if k_def > 5:
        def_items.append(f"Potassium deficit of {k_def} kg/ha")
    if s_def > 2:
        def_items.append(f"Sulphur deficit of {s_def} kg/ha")
    if zn_def > 0.5:
        def_items.append(f"Zinc deficit of {zn_def} kg/ha")

    if def_items:
        diagnosis = (f"Analysis of your {soil_type} soil for {crop_name} indicates a "
                     f"{', '.join(def_items)}. ")
    else:
        diagnosis = (f"Your {soil_type} soil shows adequate nutrient levels for {crop_name}. "
                     f"Maintenance fertilizer application is recommended. ")

    if soil_mode == 'PRECISION':
        diagnosis += "Calculations were powered by your Soil Health Card laboratory test values."
    else:
        diagnosis += f"Soil parameters were scientifically estimated based on {soil_type} regional ICAR baselines and previous cropping history."

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
            reasons.append(f"supplies {fn}% Nitrogen to eliminate the {n_def} kg/ha Nitrogen gap at ₹{cost_kg:.2f}/kg N")
        if fp > 10 and p_def > 0:
            reasons.append(f"delivers {fp}% Phosphorus for early root establishment")
        if fk > 10 and k_def > 0:
            reasons.append(f"provides {fk}% Potassium for grain filling and drought tolerance")

        if not reasons:
            reasons.append(f"supplies balanced nutrients (N:{fn}%, P:{fp}%, K:{fk}%) at economical market rates")

        item_reasons.append(f"• **{fname}** ({dose} kg/ha): Selected because it {', '.join(reasons)}.")

    # 3. Crop-Specific Special Logic Explanation
    crop_lower = crop_name.lower()
    crop_specific_note = ""
    if 'groundnut' in crop_lower:
        crop_specific_note = ("**Crop-Specific Agronomy (Groundnut):** Groundnut requires Calcium and Sulphur at pegging stage (Day 35) "
                              "for proper pod filling and oil synthesis. Gypsum application is recommended to prevent empty pods (pop pods). "
                              "Biological Nitrogen fixation via Rhizobium inoculant satisfies early Nitrogen needs, reducing synthetic Urea dependency.")
    elif 'cotton' in crop_lower:
        crop_specific_note = ("**Crop-Specific Agronomy (Cotton):** Cotton requires high Nitrogen (120-150 kg/ha) across multi-stage splits "
                              "to support boll growth. Targeted micronutrient sprays (Borax for square drop prevention & MgSO4 for leaf reddening) "
                              "and Pink Bollworm / sucking pest monitoring are essential.")
    elif 'wheat' in crop_lower:
        crop_specific_note = ("**Crop-Specific Agronomy (Wheat):** Split Nitrogen application (50% Basal, 25% Crown Root Initiation at Day 22, "
                              "25% Jointing at Day 45) maximizes fertilizer use efficiency and reduces volatilization losses before irrigation.")

    plan_rationale = (f"The **{plan_title}** was compiled using Linear Programming optimization. "
                      f"Key component breakdown:\n" + "\n".join(item_reasons))

    # 4. Soil pH & Amendment Advice
    ph_advice = ""
    if ph_val < 6.0:
        ph_advice = f"Your soil pH is acidic ({ph_val}). Agricultural lime or dolomite powder incorporation is advised before sowing to improve nutrient availability."
    elif ph_val > 7.8:
        ph_advice = f"Your soil pH is alkaline ({ph_val}). Gypsum or elemental sulphur application is recommended to reduce alkalinity and prevent micronutrient fixation."
    else:
        ph_advice = f"Soil pH ({ph_val}) is in the optimal range for {crop_name}."

    # 5. Protection & Weather Summary
    weather_summary = weather_advisory.get('current_summary', '')
    protection_count = (len(protection_plan.get('weed_management', [])) +
                        len(protection_plan.get('disease_prevention', [])) +
                        len(protection_plan.get('pest_management', [])))

    sections = [diagnosis, plan_rationale]
    if crop_specific_note:
        sections.append(crop_specific_note)
    sections.append(f"**Soil pH Note:** {ph_advice}")
    sections.append(f"**Crop Protection:** Generated {protection_count} targeted preventive/curative protection recommendations. "
                    f"Weather integration ({weather_summary}) has adjusted application timings.")

    summary_text = "\n\n".join(sections)

    return {
        'diagnosis_summary': diagnosis,
        'plan_rationale': plan_rationale,
        'ph_advice': ph_advice,
        'crop_specific_note': crop_specific_note,
        'full_explanation': summary_text,
    }
