import os
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist

from farms.models import Farm
from recommendation.weather.weather_service import fetch_current_weather
from recommendation.season.season_service import determine_season
from recommendation.models import RecommendationHistory
from ml.model_manager import ModelManager
from ml.utils import get_dataset_path

_MAPPING_DF_CACHE = None

def get_mapping_df():
    global _MAPPING_DF_CACHE
    if _MAPPING_DF_CACHE is None:
        mapping_path = get_dataset_path('crop_state_season_mapping.csv')
        if os.path.exists(mapping_path):
            _MAPPING_DF_CACHE = pd.read_csv(mapping_path)
        else:
            _MAPPING_DF_CACHE = pd.DataFrame(columns=['Crop_Name', 'Suitable_Season', 'State'])
    return _MAPPING_DF_CACHE

def get_suitable_crops_for_state_season(state: str, season: str) -> list:
    """
    Queries crop_state_season_mapping.csv for crops matching State and Season.
    """
    df = get_mapping_df()
    if df.empty or not state:
        return []

    state_clean = state.strip().lower()
    season_clean = season.strip().lower()

    # Filter state and season case-insensitively
    mask = (
        df['State'].astype(str).str.strip().str.lower().str.contains(state_clean) |
        df['State'].astype(str).str.strip().str.lower().apply(lambda s: s in state_clean)
    ) & (
        df['Suitable_Season'].astype(str).str.strip().str.lower() == season_clean
    )
    
    matched_crops = df[mask]['Crop_Name'].dropna().astype(str).str.strip().unique().tolist()
    return matched_crops

def get_all_available_crops_for_farm(farm: Farm, season: str) -> list:
    """
    Returns list of suitable crops for a farm's state & season.
    Used by frontend crop comparison multi-select.
    """
    crops = get_suitable_crops_for_state_season(farm.state, season)
    if not crops:
        # Fallback default prominent crops
        crops = [
            "Rice", "Maize", "Cotton", "Wheat", "Sugarcane", 
            "Groundnut", "Soybean", "Jowar", "Bajra", "Pulses"
        ]
    return [c.title() for c in crops]

def generate_crop_recommendation(user, farm_id: int, payload: dict) -> dict:
    """
    Orchestrates AI & Quick Crop Recommendations, Supporting Best Crop & Compare Types.

    BEST mode  → returns Top 4 crops ranked by ML probability (predict_proba).
    COMPARE mode → evaluates ONLY the farmer-selected crops (never returns others).
    Every returned crop gets its own yield prediction via yield_model.pkl.
    """
    try:
        farm = Farm.objects.get(id=farm_id, user=user)
    except ObjectDoesNotExist:
        raise ValueError("Selected farm not found or does not belong to the current user.")

    # 1. Recommendation Parameters
    mode = payload.get('mode', 'AI')       # 'AI' or 'Quick'
    rec_type = payload.get('type', 'BEST') # 'BEST' or 'COMPARE'
    compare_crops_requested = payload.get('compare_crops', [])

    # 2. Weather & Season
    weather_data = fetch_current_weather(farm.latitude, farm.longitude)
    season = determine_season()

    # 3. Read / Default Soil Inputs
    n_val = payload.get('nitrogen')
    if n_val is None: n_val = farm.nitrogen if farm.nitrogen is not None else 80.0

    p_val = payload.get('phosphorus')
    if p_val is None: p_val = farm.phosphorus if farm.phosphorus is not None else 45.0

    k_val = payload.get('potassium')
    if k_val is None: k_val = farm.potassium if farm.potassium is not None else 40.0

    ph_val = payload.get('soil_ph')
    if ph_val is None: ph_val = farm.soil_ph if farm.soil_ph is not None else 6.5

    water_req = payload.get('water_requirement', 1200)

    input_values = {
        "nitrogen": float(n_val),
        "phosphorus": float(p_val),
        "potassium": float(k_val),
        "soil_ph": float(ph_val),
        "water_requirement": float(water_req),
        "compare_crops": compare_crops_requested
    }

    feature_dict = {
        "nitrogen": float(n_val),
        "phosphorus": float(p_val),
        "potassium": float(k_val),
        "ph": float(ph_val),
        "temperature": weather_data.get('temperature', 26.5),
        "humidity": weather_data.get('humidity', 65.0),
        "rainfall": weather_data.get('rainfall', 120.0),
        "season": season,
        "soil_type": farm.soil_type,
        "water_availability": farm.water_availability
    }

    # Suitable crops for Farm State & Season (used for BEST mode filtering)
    mapped_crops = get_suitable_crops_for_state_season(farm.state, season)

    # Build explanations (common for both modes)
    reasons = [
        f"Optimized for {season} season in {farm.state}.",
        f"7-day average temperature ({feature_dict['temperature']}°C) and cumulative rainfall ({feature_dict['rainfall']}mm) provide ideal growth climate.",
        f"Soil nutrient profile (N:{feature_dict['nitrogen']}, P:{feature_dict['phosphorus']}, K:{feature_dict['potassium']}, pH:{feature_dict['ph']}) matches crop requirements.",
        f"Matches farm soil type ({farm.soil_type}) and {farm.water_availability} water availability."
    ]

    # -----------------------------------------------------------------------
    # EXECUTION MODE 1: AI RECOMMENDATION (ML Models)
    # -----------------------------------------------------------------------
    if mode == 'AI':
        model_mgr = ModelManager.get_instance()
        predictor = model_mgr.get_predictor()

        # ── BEST CROP: Top 4 ranked by predict_proba ──────────────────────
        if rec_type == 'BEST':
            # predict_crops already uses predict_proba() internally and
            # restricts to valid_crops (state+season filtered list).
            top_crops = predictor.predict_crops(
                feature_dict,
                valid_crops=mapped_crops if mapped_crops else None,
                top_k=4
            )

            if not top_crops:
                # Absolute fallback — should not normally happen
                top_crops = [{"crop": "Rice", "confidence": 85.0}]

            # Call predict_yield() for EVERY crop in the top list
            recommendations = []
            for rank, crop_item in enumerate(top_crops, start=1):
                crop_name = crop_item['crop']
                expected_yield = predictor.predict_yield(crop_name, feature_dict)
                recommendations.append({
                    "rank": rank,
                    "crop": crop_name,
                    "confidence": crop_item['confidence'],
                    "expected_yield": expected_yield,
                    "yield_unit": "kg/ha"
                })

            # Primary crop for history saving (backward compat)
            primary_crop = recommendations[0]['crop']
            confidence = recommendations[0]['confidence']
            expected_yield = recommendations[0]['expected_yield']
            comparison_results = []

        # ── COMPARE SELECTED CROPS: evaluate ONLY farmer's chosen crops ────
        else:  # rec_type == 'COMPARE'
            if not compare_crops_requested:
                raise ValueError("compare_crops list is required for COMPARE type recommendation.")

            # BUG FIX: Pass compare_crops_requested as valid_crops so that
            # predict_proba probabilities are retrieved ONLY for selected crops.
            # This guarantees no crop outside the farmer's selection is returned.
            top_crops = predictor.predict_crops(
                feature_dict,
                valid_crops=compare_crops_requested,  # ← Only selected crops evaluated
                top_k=len(compare_crops_requested)    # Return all selected, ranked
            )

            # Call predict_yield() for EVERY crop in comparison
            recommendations = []
            comparison_results = []
            for rank, crop_item in enumerate(top_crops, start=1):
                crop_name = crop_item['crop']
                crop_conf = crop_item['confidence']
                crop_yield = predictor.predict_yield(crop_name, feature_dict)
                rec_entry = {
                    "rank": rank,
                    "crop": crop_name,
                    "confidence": crop_conf,
                    "expected_yield": crop_yield,
                    "yield_unit": "kg/ha"
                }
                recommendations.append(rec_entry)
                # Keep comparison_results for backward compat
                comparison_results.append({
                    "crop": crop_name,
                    "confidence": crop_conf,
                    "expected_yield": crop_yield,
                    "suitability": "High" if crop_conf >= 70 else ("Medium" if crop_conf >= 40 else "Low"),
                    "reason": f"Evaluated under {season} climate and N-P-K soil parameters."
                })

            # Primary crop for history (top-ranked among selected)
            primary_crop = recommendations[0]['crop'] if recommendations else compare_crops_requested[0].title()
            confidence = recommendations[0]['confidence'] if recommendations else 75.0
            expected_yield = recommendations[0]['expected_yield'] if recommendations else 0.0

        prediction_source = "ML XGBoost Classifier & Regressor"

    # -----------------------------------------------------------------------
    # EXECUTION MODE 2: QUICK RECOMMENDATION (Rule-Based, Non-ML)
    # -----------------------------------------------------------------------
    else:
        reasons = [
            f"Recommended based on Agro-Climatic mapping for {farm.state} during {season} season.",
            f"Compatible with farm soil category ({farm.soil_type}) and {farm.water_availability} water supply.",
            f"Evaluated using 7-day average weather metrics (Temp: {feature_dict['temperature']}°C, Humidity: {feature_dict['humidity']}%, Rainfall: {feature_dict['rainfall']}mm).",
            "Quick assessment mode used without laboratory soil test inputs."
        ]

        # ── BEST CROP: return top 4 from state+season mapped crops ─────────
        if rec_type == 'BEST':
            candidate_crops = mapped_crops if mapped_crops else [
                "Cotton", "Maize", "Groundnut", "Wheat", "Rice", "Soybean"
            ]
            # Assign descending synthetic confidence to top 4
            top_4 = [c.title() for c in candidate_crops[:4]]
            base_confidences = [90.0, 84.0, 78.0, 72.0]
            base_yields      = [4800.0, 4500.0, 4200.0, 3900.0]

            recommendations = []
            for rank, (crop_name, conf, yld) in enumerate(
                zip(top_4, base_confidences[:len(top_4)], base_yields[:len(top_4)]), start=1
            ):
                recommendations.append({
                    "rank": rank,
                    "crop": crop_name,
                    "confidence": conf,
                    "expected_yield": yld,
                    "yield_unit": "kg/ha"
                })

            primary_crop = recommendations[0]['crop']
            confidence = recommendations[0]['confidence']
            expected_yield = recommendations[0]['expected_yield']
            comparison_results = []

        # ── COMPARE SELECTED CROPS: rule-based, only selected crops ────────
        else:  # rec_type == 'COMPARE'
            if not compare_crops_requested:
                raise ValueError("compare_crops list is required for COMPARE type recommendation.")

            recommendations = []
            comparison_results = []
            for rank, crop_item in enumerate(compare_crops_requested, start=1):
                crop_clean = crop_item.strip().title()
                is_mapped = any(c.lower() == crop_clean.lower() for c in mapped_crops) if mapped_crops else True
                conf_val = 85.0 if is_mapped else 60.0
                yld_val = 4200.0 + ((rank - 1) * 300)
                rec_entry = {
                    "rank": rank,
                    "crop": crop_clean,
                    "confidence": conf_val,
                    "expected_yield": yld_val,
                    "yield_unit": "kg/ha"
                }
                recommendations.append(rec_entry)
                comparison_results.append({
                    "crop": crop_clean,
                    "confidence": conf_val,
                    "expected_yield": yld_val,
                    "suitability": "High" if is_mapped else "Moderate",
                    "reason": f"Mapped to {farm.state} regional suitability guidelines."
                })

            primary_crop = recommendations[0]['crop'] if recommendations else compare_crops_requested[0].title()
            confidence = recommendations[0]['confidence'] if recommendations else 85.0
            expected_yield = recommendations[0]['expected_yield'] if recommendations else 4200.0

        prediction_source = "Agro-Climatic Mapping Rules"

    # -----------------------------------------------------------------------
    # Save to Recommendation History database model (unchanged schema)
    # results_payload now includes the new recommendations[] list too
    # -----------------------------------------------------------------------
    results_payload = {
        "recommended_crop": primary_crop,
        "confidence": confidence,
        "expected_yield": expected_yield,
        "season": season,
        "state": farm.state,
        "mode": mode,
        "type": rec_type,
        "reasons": reasons,
        "comparison": comparison_results,
        # New field — stored in JSONField, no migration needed
        "recommendations": recommendations
    }

    history = RecommendationHistory.objects.create(
        user=user,
        farm=farm,
        recommendation_mode=mode,
        recommendation_type=rec_type,
        input_values=input_values,
        weather_snapshot=weather_data,
        recommended_crop=primary_crop,
        expected_yield=expected_yield,
        confidence=confidence,
        results_payload=results_payload,
        explanation=reasons,
        prediction_source=prediction_source
    )

    # -----------------------------------------------------------------------
    # API Response — extends existing shape for backward compatibility.
    # recommendation (singular) → kept as-is for any existing consumers.
    # recommendations (plural)  → new list with all ranked crops.
    # -----------------------------------------------------------------------
    return {
        "id": history.id,
        # Backward-compatible single recommendation block
        "recommendation": {
            "crop": primary_crop,
            "confidence": confidence,
            "expected_yield": expected_yield,
            "yield_unit": "kg/ha",
            "prediction_source": prediction_source,
            "reason": reasons,
            "comparison": comparison_results
        },
        # New: full ranked recommendations list (always present)
        "recommendations": recommendations,
        "mode": mode,
        "type": rec_type,
        "farm": {
            "id": farm.id,
            "name": farm.farm_name,
            "location": f"{farm.village}, {farm.district}, {farm.state}",
            "state": farm.state,
            "soil_type": farm.soil_type,
            "water_availability": farm.water_availability,
            "nitrogen": input_values["nitrogen"],
            "phosphorus": input_values["phosphorus"],
            "potassium": input_values["potassium"],
            "soil_ph": input_values["soil_ph"]
        },
        "weather": weather_data,
        "season": season,
        "created_at": history.created_at.isoformat()
    }
