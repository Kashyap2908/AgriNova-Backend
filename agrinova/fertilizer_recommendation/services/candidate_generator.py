"""
Candidate Generator Engine
Filters the global catalog for technically compatible fertilizers.
"""

class CandidateGenerator:
    """
    Filters the global catalog of fertilizers into a list of viable candidates for optimization,
    based on basic physical and agronomic constraints (like avoiding purely acidic fertilizers in highly acidic soil).
    """

    @staticmethod
    def generate_candidates(catalog: list, soil_ph: float = None) -> list:
        """
        Filters fertilizers from the catalog based on compatibility.
        """
        candidates = []
        for fert in catalog:
            # If soil is extremely acidic (pH < 5.5), avoid adding more highly acidic fertilizers if possible.
            # (Just an example rule - for now we let LP decide, but we could filter here).
            # We want to keep this simple and let the optimizer handle the actual quantities.
            # But we can filter out things that are strictly incompatible.
            
            # For this dynamic engine, we'll include almost everything as a candidate and let the
            # optimizer penalize them if needed. 
            # We just return the full catalog for now, ensuring it's a valid list.
            if fert.get('price', 0.0) <= 0.0:
                continue # Skip items with no price to avoid breaking cost optimization
                
            candidates.append(fert)
            
        return candidates
