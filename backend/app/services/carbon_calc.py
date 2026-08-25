"""
EcoQuest Carbon Calculation Service
-----------------------------------
Engine for computing daily carbon emissions across different activity categories
using localized emission factors.
"""

from typing import Dict, Tuple
from app.schemas import DailyEmissionInput
from app.config import EMISSION_FACTORS


class CarbonEngine:
    """
    Engine responsible for converting raw daily activity inputs into
    CO2 equivalent (kg CO2e) emissions based on calibrated emission factors.
    """

    @staticmethod
    def calculate(data: DailyEmissionInput) -> Tuple[float, Dict[str, float]]:
        """
        Calculate total and breakdown carbon emissions for a single day's activities.

        Args:
            data (DailyEmissionInput): Input containing daily activity quantities.

        Returns:
            Tuple[float, Dict[str, float]]: A tuple of:
                - Total daily emissions in kg CO2e (rounded to 2 decimal places).
                - Breakdown dictionary mapping each activity key to its emitted kg CO2e.
        """
        # If marked as a zero-emission day, return all zeros
        if data.is_zero_emission:
            breakdown: Dict[str, float] = {activity_key: 0.0 for activity_key in EMISSION_FACTORS}
            return 0.0, breakdown

        breakdown: Dict[str, float] = {}

        # Compute emissions for each activity category defined in EMISSION_FACTORS
        for activity_key, factor in EMISSION_FACTORS.items():
            activity_val: float = getattr(data, activity_key, 0.0)
            breakdown[activity_key] = round(activity_val * factor, 2)

        # Calculate sum of all activity emissions
        total_emissions: float = round(sum(breakdown.values()), 2)

        return total_emissions, breakdown
