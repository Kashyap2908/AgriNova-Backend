from recommendation.views import get_area_unit_info

class ProfitEngine:
    """
    Computes financial metrics, scenario simulations (Best/Average/Worst),
    and risk analysis for Profit Analysis module.
    Uses temporary cost objects only. Never mutates CSV, DB, or caches directly.
    """

    @staticmethod
    def calculate_profit_analysis(
        farm,
        crop: str,
        expected_yield_total_quintals: float,
        predicted_market_price: float,
        base_cost_dict: dict,
        custom_cost_overrides: dict = None
    ) -> dict:
        area_val = float(farm.farm_area or 1.0)
        unit_info = get_area_unit_info(area_val, farm.area_unit)

        unit_label = unit_info["display_unit"]
        per_unit_multiplier = unit_info["acres_per_unit"]

        # Baseline per-unit costs from cost dataset (dataset costs are per acre)
        base_seed_unit = base_cost_dict.get('seed_cost_per_acre', 2000.0) * per_unit_multiplier
        base_fert_unit = base_cost_dict.get('fertilizer_cost_per_acre', 4500.0) * per_unit_multiplier
        base_labour_unit = base_cost_dict.get('labour_cost_per_acre', 8500.0) * per_unit_multiplier
        base_irrig_unit = base_cost_dict.get('irrigation_cost_per_acre', 2500.0) * per_unit_multiplier
        base_mach_unit = base_cost_dict.get('machinery_cost_per_acre', 3500.0) * per_unit_multiplier
        base_other_unit = base_cost_dict.get('other_cost_per_acre', 1500.0) * per_unit_multiplier

        # Create temporary cost object (per-unit and total farm)
        temp_costs = {
            "seed_cost": base_seed_unit * area_val,
            "fertilizer_cost": base_fert_unit * area_val,
            "labour_cost": base_labour_unit * area_val,
            "irrigation_cost": base_irrig_unit * area_val,
            "machinery_cost": base_mach_unit * area_val,
            "other_cost": base_other_unit * area_val,
            "seed_cost_unit": base_seed_unit,
            "fertilizer_cost_unit": base_fert_unit,
            "labour_cost_unit": base_labour_unit,
            "irrigation_cost_unit": base_irrig_unit,
            "machinery_cost_unit": base_mach_unit,
            "other_cost_unit": base_other_unit,
        }

        # Apply custom cost overrides if provided by farmer
        if custom_cost_overrides and isinstance(custom_cost_overrides, dict):
            for k in ['seed_cost', 'fertilizer_cost', 'labour_cost', 'irrigation_cost', 'machinery_cost', 'other_cost']:
                if k in custom_cost_overrides:
                    val = float(custom_cost_overrides[k])
                    val = max(0.0, val) # Prevent negative values
                    temp_costs[k] = val
                    temp_costs[f"{k}_unit"] = val / area_val if area_val > 0 else val

        total_cost = (
            temp_costs['seed_cost'] +
            temp_costs['fertilizer_cost'] +
            temp_costs['labour_cost'] +
            temp_costs['irrigation_cost'] +
            temp_costs['machinery_cost'] +
            temp_costs['other_cost']
        )
        temp_costs['total_cost'] = total_cost
        temp_costs['total_cost_unit'] = total_cost / area_val if area_val > 0 else total_cost

        # Primary Financial Calculations
        price = max(0.0, float(predicted_market_price))
        yield_total = max(0.0, float(expected_yield_total_quintals))

        gross_income = round(yield_total * price, 2)
        net_profit = round(gross_income - total_cost, 2)

        roi = round((net_profit / total_cost * 100.0), 2) if total_cost > 0 else 0.0
        profit_margin = round((net_profit / gross_income * 100.0), 2) if gross_income > 0 else 0.0
        break_even_price = round(total_cost / yield_total, 2) if yield_total > 0 else 0.0

        # Scenario Analysis (Best / Average / Worst)
        # Average Case
        avg_yield = yield_total
        avg_price = price
        avg_gross = gross_income
        avg_net = net_profit
        avg_roi = roi

        # Best Case (+15% yield, +10% price)
        best_yield = round(yield_total * 1.15, 2)
        best_price = round(price * 1.10, 2)
        best_gross = round(best_yield * best_price, 2)
        best_net = round(best_gross - total_cost, 2)
        best_roi = round((best_net / total_cost * 100.0), 2) if total_cost > 0 else 0.0

        # Worst Case (-15% yield, -10% price)
        worst_yield = round(yield_total * 0.85, 2)
        worst_price = round(price * 0.90, 2)
        worst_gross = round(worst_yield * worst_price, 2)
        worst_net = round(worst_gross - total_cost, 2)
        worst_roi = round((worst_net / total_cost * 100.0), 2) if total_cost > 0 else 0.0

        scenarios = {
            "average_case": {
                "label": "Average Expected Case",
                "yield_quintal": avg_yield,
                "market_price": avg_price,
                "gross_income": avg_gross,
                "net_profit": avg_net,
                "roi": avg_roi
            },
            "best_case": {
                "label": "Best Case Scenario (+15% Yield, +10% Price)",
                "yield_quintal": best_yield,
                "market_price": best_price,
                "gross_income": best_gross,
                "net_profit": best_net,
                "roi": best_roi
            },
            "worst_case": {
                "label": "Worst Case Scenario (-15% Yield, -10% Price)",
                "yield_quintal": worst_yield,
                "market_price": worst_price,
                "gross_income": worst_gross,
                "net_profit": worst_net,
                "roi": worst_roi
            }
        }

        # Risk Analysis
        if roi >= 40.0 and net_profit > 0:
            risk_level = "Low"
            risk_description = "High return on investment with strong financial margin against price fluctuations."
        elif roi >= 15.0 and net_profit > 0:
            risk_level = "Medium"
            risk_description = "Moderate profitability. Monitor market trend and input costs closely."
        else:
            risk_level = "High"
            risk_description = "Low or negative margin. High vulnerability to market price dips or yield reductions."

        risk_analysis = {
            "level": risk_level,
            "description": risk_description,
            "factors": [
                f"Break-even price is ₹{break_even_price}/Quintal vs predicted ₹{price}/Quintal.",
                f"Worst case net profit estimated at ₹{worst_net:,.2f} ({worst_roi}% ROI).",
                f"Calculated under {farm.water_availability.lower()} water availability in {farm.state}."
            ]
        }

        # Final Recommendation
        if net_profit > 0:
            final_recommendation = (
                f"{crop} cultivation on your {area_val} {unit_label} farm is financially viable. "
                f"With an investment of ₹{total_cost:,.2f}, expected net profit is ₹{net_profit:,.2f} "
                f"({roi}% ROI) at a predicted 3-month harvest price of ₹{price:,.2f}/Quintal."
            )
        else:
            final_recommendation = (
                f"Cultivating {crop} under current cost structure presents financial risk with a net deficit of ₹{abs(net_profit):,.2f}. "
                f"Consider customizing/reducing input costs or selecting an alternative recommended crop."
            )

        return {
            "farm_info": {
                "farm_id": farm.id,
                "farm_name": farm.farm_name,
                "state": farm.state,
                "district": farm.district,
                "farm_area": area_val,
                "farm_area_unit": unit_label
            },
            "crop": crop,
            "expected_yield_total_quintals": yield_total,
            "predicted_market_price_3m": price,
            "cost_source": {
                "source_name": base_cost_dict.get("source", "Government Benchmark"),
                "last_updated": base_cost_dict.get("last_updated", "2024-2025"),
                "is_customized": bool(custom_cost_overrides)
            },
            "cost_breakdown": temp_costs,
            "financial_summary": {
                "total_investment": round(total_cost, 2),
                "gross_income": gross_income,
                "net_profit": net_profit,
                "roi": roi,
                "profit_margin": profit_margin,
                "break_even_price": break_even_price
            },
            "scenarios": scenarios,
            "risk_analysis": risk_analysis,
            "final_recommendation": final_recommendation
        }
