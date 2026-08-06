"""
Recommendation Ranking Engine
Scores and ranks optimized fertilizer plans based on multiple agronomic and economic criteria.
"""

class RankingEngine:
    """
    Ranks LP-generated solutions using a weighted scoring model.
    Nutrient Match: 40%
    Cost: 20%
    Crop Compatibility: 10%
    Soil Compatibility: 10%
    Weather Compatibility: 10%
    Application Simplicity: 5%
    Availability: 5%
    """

    @staticmethod
    def rank_plans(plans: list, crop: str, soil_ph: float, weather_summary: dict) -> list:
        for plan in plans:
            score = 0.0
            
            items = plan['items']
            total_items = len(items)
            
            # 1. Nutrient Match (40%)
            # Since these are LP solutions, they perfectly meet the nutrient requirements.
            # But the "Balanced" plan might have less excess. We'll give high marks generally.
            if plan['strategy'] == 'balanced':
                score += 40.0
            else:
                score += 35.0
                
            # 2. Cost (20%)
            if plan['strategy'] == 'economical':
                score += 20.0
            else:
                score += 15.0
                
            # 3. Crop Compatibility (10%)
            # Basic checking if complex/organics match certain crops (just some heuristics, not filtering)
            crop_score = 7.0
            fert_names = " ".join([i['fertilizer']['name'].lower() for i in items])
            if any(c in crop.lower() for c in ['vegetable', 'potato', 'tomato']) and 'potash' in fert_names:
                crop_score = 10.0
            elif any(c in crop.lower() for c in ['wheat', 'rice', 'maize']) and 'dap' in fert_names:
                crop_score = 10.0
            score += crop_score
            
            # 4. Soil Compatibility (10%)
            soil_score = 10.0
            if soil_ph is not None:
                if soil_ph < 6.0 and 'super phosphate' in fert_names:
                    soil_score = 10.0
                elif soil_ph < 6.0 and 'dap' in fert_names:
                    soil_score -= 2.0 # DAP is less ideal in highly acidic without amendment
            score += soil_score
            
            # 5. Weather Compatibility (10%)
            # Heavy rain -> granular or slow release might be better (neem coated urea)
            weather_score = 10.0
            if 'heavy' in weather_summary.get('condition', '').lower() and 'neem coated' in fert_names:
                weather_score = 10.0
            score += weather_score
            
            # 6. Application Simplicity (5%)
            # Fewer items is better
            simp_score = 5.0
            if total_items > 3:
                simp_score = max(1.0, 5.0 - (total_items - 3))
            if plan['strategy'] == 'application_easy':
                simp_score = 5.0
            score += simp_score
            
            # 7. Availability (5%)
            score += 5.0 # Assuming all in catalog are available
            
            plan['score'] = round(score, 1)

        # Sort descending by score
        return sorted(plans, key=lambda x: x['score'], reverse=True)
