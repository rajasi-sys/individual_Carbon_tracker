"""
EcoQuest Gamification Service
-----------------------------
Encapsulates the business logic for calculating tree stages, levels,
and automated conditions for unlocking user achievements and badges.
"""

from sqlalchemy.orm import Session
from app.models import UserModel, UserBadgeModel
from app.config import CITY_BENCHMARKS

# Virtual Tree Stage Mapping
TREE_STAGE_MAP = {
    1: "🌱 Seedling",
    2: "🌿 Sprout",
    3: "🪴 Sapling",
    4: "🌳 Tree",
    5: "🌲🌲 Forest"
}


class GamificationService:
    """Service handling gamification logic such as XP, levels, tree growth, and badges."""

    @staticmethod
    def get_tree_stage(xp: int) -> tuple[int, str]:
        """
        Evaluate virtual tree stage based on accumulated XP.
        
        Args:
            xp (int): Total eco points.
            
        Returns:
            tuple[int, str]: Stage integer and its corresponding emoji icon string.
        """
        if xp > 2000:
            stage = 5
        elif xp > 1200:
            stage = 4
        elif xp > 600:
            stage = 3
        elif xp > 200:
            stage = 2
        else:
            stage = 1
            
        return stage, TREE_STAGE_MAP[stage]

    @staticmethod
    def calculate_level(xp: int) -> int:
        """
        Calculate user level from total XP.
        Level up occurs every 500 XP.
        """
        return (xp // 500) + 1

    @staticmethod
    def evaluate_badges(
        user: UserModel, 
        daily_emissions: float, 
        monthly_savings: float, 
        db: Session
    ) -> list[dict]:
        """
        Evaluate and unlock badges for the user based on their current assessment.
        
        Args:
            user (UserModel): Current user model.
            daily_emissions (float): Calculated daily CO2 emissions.
            monthly_savings (float): Calculated monthly financial savings.
            db (Session): Database session to query and commit new badges.
            
        Returns:
            list[dict]: A list of newly unlocked badge dictionaries.
        """
        new_badges = []
        
        # Query existing badges for this user
        existing_badges = db.query(UserBadgeModel).filter(UserBadgeModel.user_id == user.id).all()
        unlocked_badge_names = {badge.badge_name for badge in existing_badges}
        
        city_config = CITY_BENCHMARKS.get(user.city) or CITY_BENCHMARKS.get("Default", {})
        city_daily_avg = city_config.get("monthly_avg_co2", 250.0) / 30.0
        
        # Helper to grant badge
        def grant_badge(name: str, desc: str):
            if name not in unlocked_badge_names:
                new_badge = UserBadgeModel(
                    user_id=user.id,
                    badge_name=name,
                    badge_description=desc
                )
                db.add(new_badge)
                new_badges.append({"badge_name": name, "badge_description": desc})
                unlocked_badge_names.add(name)

        # 1. "Eco Pioneer" Badge
        if "Eco Pioneer" not in unlocked_badge_names:
            grant_badge("Eco Pioneer", "Logged your first eco audit!")
            
        # 2. "Smart Saver" Badge
        if daily_emissions == 0.0 or daily_emissions < city_daily_avg:
            grant_badge("Smart Saver", "Kept daily emissions strictly under city benchmark limit!")
            
        # 3. "Energy Investor" Badge
        if (monthly_savings * 12) > 100:
            grant_badge("Energy Investor", "Identified over 100 in potential annual utility savings!")
            
        # Commit all new badges to the database if any were unlocked
        if new_badges:
            db.commit()
            
        return new_badges
