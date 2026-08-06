"""
Fertilizer Combination Optimizer Engine
Uses Mathematical Optimization (Linear Programming) to select the best fertilizers dynamically.
"""

import numpy as np
from scipy.optimize import linprog
import logging

logger = logging.getLogger(__name__)


class CombinationOptimizer:
    """
    Optimizes fertilizer selection using Linear Programming.
    Solves for N, P, K requirements using available fertilizers from the catalog.
    """

    @staticmethod
    def optimize(target_n: float, target_p: float, target_k: float, catalog: list, strategy: str = 'economical') -> list:
        """
        Runs an LP solver to find the optimal mix of fertilizers.
        Strategy options: 'economical', 'balanced', 'application_easy'
        Returns a list of items: [{'fertilizer': fert_dict, 'dose_kg_ha': float}]
        """
        # If no nutrients are required, return empty list
        if target_n <= 0 and target_p <= 0 and target_k <= 0:
            return []

        # Filter out fertilizers with no N, P, K (like soil conditioners, if any) unless they are needed for pH
        valid_ferts = [f for f in catalog if (f['n_pct'] > 0 or f['p_pct'] > 0 or f['k_pct'] > 0)]
        if not valid_ferts:
            return []

        num_vars = len(valid_ferts)
        
        # We want: (x * pct) >= target => - (x * pct/100) <= -target
        A_ub = np.zeros((3, num_vars))
        b_ub = np.array([-target_n, -target_p, -target_k])
        
        c = np.zeros(num_vars)
        
        for i, fert in enumerate(valid_ferts):
            # Nutrients supplied per 1 kg of fertilizer
            A_ub[0, i] = - (fert['n_pct'] / 100.0)
            A_ub[1, i] = - (fert['p_pct'] / 100.0)
            A_ub[2, i] = - (fert['k_pct'] / 100.0)
            
            # Objective coefficients based on strategy
            if strategy == 'economical':
                # Minimize total cost
                c[i] = fert['price']
            elif strategy == 'balanced':
                # Minimize excess nutrients + cost penalty.
                # A balanced approach tries to hit the exact target without massive over-application.
                # Total nutrient excess = (supplied - target). 
                # To minimize excess, we minimize total kg of N, P, K supplied, scaled by a cost factor.
                # Weighting: 70% on minimizing total nutrient sum, 30% on cost.
                total_nutrient_pct = fert['n_pct'] + fert['p_pct'] + fert['k_pct']
                c[i] = (fert['price'] * 0.3) + ((100.0 - total_nutrient_pct) * 0.7)
            elif strategy == 'application_easy':
                # Minimize total physical quantity (bulk). So just minimize x_i directly.
                c[i] = 1.0 + (fert['price'] * 0.05) # Add small price penalty to break ties
            else:
                c[i] = fert['price']

        # Bounds: dose >= 0 for all x
        bounds = [(0, None) for _ in range(num_vars)]

        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
            
            if res.success:
                solution_items = []
                for i, amount in enumerate(res.x):
                    if amount >= 1.0: # Only include if dose is at least 1 kg/ha
                        solution_items.append({
                            'fertilizer': valid_ferts[i],
                            'dose_kg_ha': round(float(amount), 1)
                        })
                return solution_items
            else:
                logger.warning(f"LP Solver failed: {res.message}")
                return []
        except Exception as e:
            logger.error(f"Error in CombinationOptimizer: {e}")
            return []

    @staticmethod
    def generate_all_plans(target_n: float, target_p: float, target_k: float, catalog: list) -> list:
        """
        Generates multiple distinct plans using different objective strategies.
        """
        plans = []
        
        # 1. Economical Plan
        eco_items = CombinationOptimizer.optimize(target_n, target_p, target_k, catalog, 'economical')
        if eco_items:
            plans.append({
                'title': 'Economical Plan',
                'description': 'Mathematically optimized for the absolute lowest cost to meet requirements.',
                'items': eco_items,
                'tag': 'MOST ECONOMICAL',
                'strategy': 'economical'
            })
            
        # 2. Balanced Plan
        bal_items = CombinationOptimizer.optimize(target_n, target_p, target_k, catalog, 'balanced')
        if bal_items:
            # Check if it's identical to eco
            if not CombinationOptimizer._is_duplicate(eco_items, bal_items):
                plans.append({
                    'title': 'Balanced Efficiency Plan',
                    'description': 'Balances cost with minimizing excess nutrient application (less wastage).',
                    'items': bal_items,
                    'tag': 'BALANCED',
                    'strategy': 'balanced'
                })
                
        # 3. Easy Application Plan
        easy_items = CombinationOptimizer.optimize(target_n, target_p, target_k, catalog, 'application_easy')
        if easy_items:
            if not CombinationOptimizer._is_duplicate(eco_items, easy_items) and not CombinationOptimizer._is_duplicate(bal_items, easy_items):
                plans.append({
                    'title': 'Easy Application Plan',
                    'description': 'Minimizes the total physical bulk (kg) of fertilizers you have to handle.',
                    'items': easy_items,
                    'tag': 'EASY APPLICATION',
                    'strategy': 'application_easy'
                })
                
        return plans
        
    @staticmethod
    def _is_duplicate(plan_a: list, plan_b: list) -> bool:
        if not plan_a or not plan_b:
            return False
        if len(plan_a) != len(plan_b):
            return False
        
        a_ferts = {item['fertilizer']['name']: item['dose_kg_ha'] for item in plan_a}
        b_ferts = {item['fertilizer']['name']: item['dose_kg_ha'] for item in plan_b}
        
        if set(a_ferts.keys()) != set(b_ferts.keys()):
            return False
            
        # Check if quantities are roughly the same (within 5 kg)
        for k in a_ferts.keys():
            if abs(a_ferts[k] - b_ferts[k]) > 5.0:
                return False
        return True
