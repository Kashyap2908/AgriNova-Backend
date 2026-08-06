import logging

logger = logging.getLogger(__name__)


class DeficiencyCalculator:
    """
    Calculator for soil nutrient deficiency relative to crop ideal requirements.
    """

    @staticmethod
    def calculate_deficiency(ideal: dict, actual: dict) -> dict:
        """
        Calculates NPK deficiency based on ideal requirements vs actual/estimated soil values.
        Returns dict: {'N': float, 'P': float, 'K': float}
        Ensures negative values are capped at 0.0.
        """
        ideal_n = float(ideal.get('N', 0.0) if ideal else 0.0)
        ideal_p = float(ideal.get('P', 0.0) if ideal else 0.0)
        ideal_k = float(ideal.get('K', 0.0) if ideal else 0.0)

        actual_n = float(actual.get('N', 0.0) if actual else 0.0)
        actual_p = float(actual.get('P', 0.0) if actual else 0.0)
        actual_k = float(actual.get('K', 0.0) if actual else 0.0)

        return {
            'N': float(round(max(0.0, ideal_n - actual_n), 2)),
            'P': float(round(max(0.0, ideal_p - actual_p), 2)),
            'K': float(round(max(0.0, ideal_k - actual_k), 2))
        }
