"""
EcoQuest Backend Configuration
------------------------------
Global application settings, security configurations, emission factors,
and city benchmark pricing for carbon footprint calculations.
"""

from typing import Dict, Any
from pydantic import BaseModel

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        """Global security and application configuration settings loaded from environment variables or defaults."""
        SECRET_KEY: str = "ECOQUEST_SUPER_SECRET_KEY_2026"
        ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore"
        )

except ImportError:
    # Fallback to Pydantic BaseModel if pydantic-settings is not installed
    class Settings(BaseModel):  # type: ignore
        """Global security and application configuration settings loaded from defaults."""
        SECRET_KEY: str = "ECOQUEST_SUPER_SECRET_KEY_2026"
        ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 120


# Singleton settings instance
settings = Settings()

# Direct export constants for simplified importing across modules
SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM: str = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Emission Factor Constants (kg CO2e per unit)
EMISSION_FACTORS: Dict[str, float] = {
    "electricity_kwh": 0.85,
    "petrol_car_km": 0.17,
    "diesel_car_km": 0.19,
    "bus_km": 0.05,
    "flight_km": 0.25,
    "lpg_cylinder": 42.50,
    "meat_meals": 2.50,
}

# Individual constant exports for convenience
EMISSION_ELECTRICITY_KWH: float = EMISSION_FACTORS["electricity_kwh"]
EMISSION_PETROL_CAR_KM: float = EMISSION_FACTORS["petrol_car_km"]
EMISSION_DIESEL_CAR_KM: float = EMISSION_FACTORS["diesel_car_km"]
EMISSION_BUS_KM: float = EMISSION_FACTORS["bus_km"]
EMISSION_FLIGHT_KM: float = EMISSION_FACTORS["flight_km"]
EMISSION_LPG_CYLINDER: float = EMISSION_FACTORS["lpg_cylinder"]
EMISSION_MEAT_MEALS: float = EMISSION_FACTORS["meat_meals"]

# City Benchmarks & Currency Dictionary (CITY_BENCHMARKS)
CITY_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "Mumbai": {
        "symbol": "₹",
        "code": "INR",
        "monthly_avg_co2": 210.0,
        "elec_rate": 8.50,    # INR/kWh
        "fuel_rate": 104.0,   # INR/liter
        "lpg_rate": 900.0,    # INR/cylinder
    },
    "Delhi": {
        "symbol": "₹",
        "code": "INR",
        "monthly_avg_co2": 230.0,
        "elec_rate": 7.00,    # INR/kWh
        "fuel_rate": 95.0,    # INR/liter
        "lpg_rate": 850.0,    # INR/cylinder
    },
    "London": {
        "symbol": "£",
        "code": "GBP",
        "monthly_avg_co2": 320.0,
        "elec_rate": 0.28,    # GBP/kWh
        "fuel_rate": 1.45,    # GBP/liter
        "lpg_rate": 35.0,     # GBP/cylinder
    },
    "New York": {
        "symbol": "$",
        "code": "USD",
        "monthly_avg_co2": 450.0,
        "elec_rate": 0.18,    # USD/kWh
        "fuel_rate": 1.10,    # USD/liter
        "lpg_rate": 30.0,     # USD/cylinder
    },
    "Default": {
        "symbol": "₹",
        "code": "INR",
        "monthly_avg_co2": 250.0,
        "elec_rate": 8.00,    # INR/kWh
        "fuel_rate": 100.0,   # INR/liter
        "lpg_rate": 880.0,    # INR/cylinder
    },
}
