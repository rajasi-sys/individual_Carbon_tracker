"""
EcoQuest Pydantic Schemas
-------------------------
Data validation models and response serializers for FastAPI endpoints.
Uses Pydantic v2 conventions.
"""

from datetime import datetime, date
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# ==========================================
# 1. Authentication Schemas
# ==========================================

class UserCreate(BaseModel):
    """Payload for user account registration."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """OAuth2 JWT access token response structure."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Payload data extracted from JWT token claims."""
    email: Optional[str] = None


# ==========================================
# 2. Profile & Demographic Schemas
# ==========================================

class ProfileUpdate(BaseModel):
    """Payload for updating user profile metrics."""
    name: str = Field("Eco Citizen", min_length=1)
    age: int = Field(20, ge=1, le=120)
    gender: str = Field("Not Specified")
    city: str = Field("Default")
    household_size: int = Field(1, ge=1)


class UserOut(BaseModel):
    """Response schema representing a registered user."""
    id: int
    email: EmailStr
    name: str
    age: int
    gender: str
    city: str
    household_size: int
    eco_points: int
    streak_count: int
    level: int
    tree_stage: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 3. Emission Logging & Calculation Schemas
# ==========================================

class DailyEmissionInput(BaseModel):
    """Payload for logging daily consumption and activity metrics."""
    date_str: str = Field(default_factory=lambda: date.today().strftime("%Y-%m-%d"))
    electricity_kwh: float = Field(0.0, ge=0.0)
    petrol_car_km: float = Field(0.0, ge=0.0)
    diesel_car_km: float = Field(0.0, ge=0.0)
    bus_km: float = Field(0.0, ge=0.0)
    flight_km: float = Field(0.0, ge=0.0)
    lpg_cylinder: float = Field(0.0, ge=0.0)
    meat_meals: float = Field(0.0, ge=0.0)
    is_zero_emission: bool = False


# ==========================================
# 4. Gamification & Response Schemas
# ==========================================

class BadgeOut(BaseModel):
    """Response structure for user achievement badges."""
    badge_name: str
    badge_description: str
    unlocked_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaderboardUserOut(BaseModel):
    """Response structure for leaderboard ranking entries."""
    rank: int
    name: str
    city: str
    xp: int
    level: int
    streak: int
    tree_icon: str


class FinancialsOut(BaseModel):
    """Financial savings and spend metrics."""
    currency_symbol: str
    currency_code: str
    monthly_spend: float
    monthly_savings: float
    yearly_roi: float


class DailyLockResponse(BaseModel):
    """Output structure returned upon logging/locking daily carbon emissions."""
    date_str: str
    is_zero_emission: bool
    total_emissions_kg_co2: float
    city_daily_avg_kg_co2: float
    city_name: str
    financials: FinancialsOut
    breakdown: Dict[str, float]
    xp_earned: int
    total_xp: int
    level: int
    streak_days: int
    tree_stage: int
