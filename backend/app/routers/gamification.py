"""
EcoQuest Gamification Router
----------------------------
Handles global leaderboards and individual user gamification stats,
including XP, tree growth, carbon savings, and unlocked badges.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserModel, UserBadgeModel, AssessmentModel
from app.security import get_current_user
from app.services import GamificationService
from app.config import CITY_BENCHMARKS

router = APIRouter(prefix="/api/v1", tags=["Gamification & Leaderboard"])

@router.get("/leaderboard")
def get_global_leaderboard(db: Session = Depends(get_db)):
    """
    Retrieve the top 10 users ranked by total eco points.
    """
    top_users = (
        db.query(UserModel)
        .order_by(UserModel.eco_points.desc())
        .limit(10)
        .all()
    )
    
    leaderboard = []
    for rank_idx, user in enumerate(top_users, start=1):
        _, tree_icon = GamificationService.get_tree_stage(user.eco_points)
        
        leaderboard.append({
            "rank": rank_idx,
            "name": user.name,
            "city": user.city,
            "xp": user.eco_points,
            "level": user.level,
            "streak": user.streak_count,
            "tree_icon": tree_icon
        })
        
    return leaderboard


@router.get("/user/stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve gamification stats for the current user, including accumulated
    carbon savings, tree stage, and unlocked achievement badges.
    """
    # Query all assessments logged by the user
    assessments = (
        db.query(AssessmentModel)
        .filter(AssessmentModel.user_id == current_user.id)
        .all()
    )
    total_assessments_logged = len(assessments)
    
    # Calculate city daily baseline for carbon savings
    city_config = CITY_BENCHMARKS.get(current_user.city) or CITY_BENCHMARKS.get("Default", {})
    city_daily_avg = city_config.get("monthly_avg_co2", 250.0) / 30.0
    
    # Compute total carbon and money saved
    total_carbon_saved = 0.0
    total_money_saved = 0.0
    
    for assessment in assessments:
        # Carbon saved: Difference between city average and actual emissions (floored at 0)
        carbon_diff = city_daily_avg - assessment.total_emissions
        if carbon_diff > 0:
            total_carbon_saved += carbon_diff
            
        # Money saved: Assuming a target 20% savings on the assessed monthly cost
        total_money_saved += assessment.monthly_cost * 0.20

    # Retrieve all unlocked badges
    badges = (
        db.query(UserBadgeModel)
        .filter(UserBadgeModel.user_id == current_user.id)
        .all()
    )
    
    badges_list = [
        {
            "badge_name": b.badge_name,
            "badge_description": b.badge_description,
            "unlocked_at": b.unlocked_at
        }
        for b in badges
    ]
    
    # Determine tree stage and icon
    stage_integer, icon_string = GamificationService.get_tree_stage(current_user.eco_points)
    
    return {
        "email": current_user.email,
        "name": current_user.name,
        "city": current_user.city,
        "xp": current_user.eco_points,
        "level": current_user.level,
        "streak_count": current_user.streak_count,
        "tree_stage": stage_integer,
        "tree_icon": icon_string,
        "total_assessments_logged": total_assessments_logged,
        "total_carbon_saved_kg": round(total_carbon_saved, 2),
        "total_money_saved": round(total_money_saved, 2),
        "badges": badges_list
    }
