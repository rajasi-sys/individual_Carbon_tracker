"""
EcoQuest Financial Analytics Service
------------------------------------
Dynamic calculation engine to translate energy & fuel consumption into
localized utility costs, potential monthly savings, and yearly ROI projections.
"""

from typing import Dict, Any
from app.schemas import DailyEmissionInput
from app.config import CITY_BENCHMARKS


class DynamicFinancialEngine:
    """
    Financial calculation engine factoring in city-specific utility rates
    for electricity, automotive fuels, and domestic cooking gas (LPG).
    """

    @staticmethod
    def calculate_local_costs(data: DailyEmissionInput, city: str) -> Dict[str, Any]:
        """
        Compute localized monthly expenditure, savings potential, and annual ROI.

        Args:
            data (DailyEmissionInput): Input containing consumption values.
            city (str): User's selected or default city for localized tariffs.

        Returns:
            Dict[str, Any]: Financial metrics containing currency details,
                            estimated monthly spend, potential savings, and projected ROI.
        """
        # Lookup city configuration with fallback to 'Default' benchmark
        city_config: Dict[str, Any] = CITY_BENCHMARKS.get(city) or CITY_BENCHMARKS.get("Default", {})

        currency_symbol: str = city_config.get("symbol", "₹")
        currency_code: str = city_config.get("code", "INR")

        # Zero emission day returns zeroed financial impact
        if data.is_zero_emission:
            return {
                "currency_symbol": currency_symbol,
                "currency_code": currency_code,
                "monthly_spend": 0.0,
                "monthly_savings": 0.0,
                "yearly_roi": 0.0,
            }

        elec_rate: float = float(city_config.get("elec_rate", 8.00))
        fuel_rate: float = float(city_config.get("fuel_rate", 100.00))
        lpg_rate: float = float(city_config.get("lpg_rate", 880.00))

        # 1. Electricity spend: kWh * local rate per kWh
        elec_cost: float = data.electricity_kwh * elec_rate

        # 2. Fuel spend: Assuming standard fuel economy of ~12 km/L
        # Fuel Liters = petrol_car_km / 12.0
        fuel_cost: float = (data.petrol_car_km / 12.0) * fuel_rate

        # 3. Cooking Gas spend: cylinder count * cost per cylinder
        lpg_cost: float = data.lpg_cylinder * lpg_rate

        # Total monthly estimated spend
        total_monthly: float = round(elec_cost + fuel_cost + lpg_cost, 2)

        # Potential monthly savings targeting a 20% eco-optimization cut
        monthly_savings: float = round(total_monthly * 0.20, 2)

        # Projected 12-month return on investment / conservation savings
        yearly_roi: float = round(monthly_savings * 12.0, 2)

        return {
            "currency_symbol": currency_symbol,
            "currency_code": currency_code,
            "monthly_spend": total_monthly,
            "monthly_savings": monthly_savings,
            "yearly_roi": yearly_roi,
        }
