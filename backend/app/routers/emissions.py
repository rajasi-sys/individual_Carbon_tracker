"""
EcoQuest Emissions Router
-------------------------
Handles daily carbon emission logging, benchmarking, and gamification logic.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserModel, AssessmentModel
from app.schemas import DailyEmissionInput, DailyLockResponse
from app.security import get_current_user
from app.config import CITY_BENCHMARKS
from app.services.carbon_calc import CarbonEngine
from app.services.financial import DynamicFinancialEngine

router = APIRouter(prefix="/api/v1/emissions", tags=["Emissions & Benchmarks"])

@router.post("/lock-daily", response_model=DailyLockResponse)
def lock_daily_emissions(
    data: DailyEmissionInput,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Log and lock daily emissions, calculate financials, and update gamification metrics.
    """
    # a. Calculate emissions using CarbonEngine
    total_emissions, breakdown = CarbonEngine.calculate(data)
    
    # b. Calculate financial metrics using DynamicFinancialEngine
    financials = DynamicFinancialEngine.calculate_local_costs(data, current_user.city)
    
    # c. Retrieve user's city configuration from CITY_BENCHMARKS (fallback to "Default")
    city_config = CITY_BENCHMARKS.get(current_user.city) or CITY_BENCHMARKS.get("Default", {})
    
    # d. Calculate city daily average baseline
    city_daily_avg = round(city_config.get("monthly_avg_co2", 250.0) / 30.0, 2)
    
    # e. Update user streak logic
    xp_earned = 100  # Base XP points
    
    if data.is_zero_emission or total_emissions < city_daily_avg:
        current_user.streak_count += 1
        xp_earned += 150  # Bonus XP
    else:
        current_user.streak_count = max(1, current_user.streak_count)
        
    # f. Grant base + bonus XP points
    current_user.eco_points += xp_earned
    
    # g. Recalculate level
    current_user.level = (current_user.eco_points // 500) + 1
    
    # h. Update virtual tree stage based on total XP (eco_points)
    if current_user.eco_points > 2000:
        current_user.tree_stage = 5
    elif current_user.eco_points > 1200:
        current_user.tree_stage = 4
    elif current_user.eco_points > 600:
        current_user.tree_stage = 3
    elif current_user.eco_points > 200:
        current_user.tree_stage = 2
    else:
        current_user.tree_stage = 1
        
    # i. Save assessment log to database
    new_assessment = AssessmentModel(
        user_id=current_user.id,
        date_str=data.date_str,
        total_emissions=total_emissions,
        monthly_cost=financials["monthly_spend"],
        is_zero_emission=data.is_zero_emission
    )
    
    db.add(new_assessment)
    db.commit()
    db.refresh(current_user)
    
    # j. Return DailyLockResponse containing all calculated metrics
    return DailyLockResponse(
        date_str=data.date_str,
        is_zero_emission=data.is_zero_emission,
        total_emissions_kg_co2=total_emissions,
        city_daily_avg_kg_co2=city_daily_avg,
        city_name=current_user.city,
        financials=financials,
        breakdown=breakdown,
        xp_earned=xp_earned,
        total_xp=current_user.eco_points,
        level=current_user.level,
        streak_days=current_user.streak_count,
        tree_stage=current_user.tree_stage
    )
