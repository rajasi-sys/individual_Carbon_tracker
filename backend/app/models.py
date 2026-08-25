"""
EcoQuest Database ORM Models
----------------------------
Defines SQLAlchemy ORM models for users, carbon footprint assessments,
gamification badges, and uploaded utility bills.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class UserModel(Base):
    """
    User account model storing authentication credentials, profile demographics,
    and gamification progress (eco points, streak, tree stage, level).
    """
    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Auth Credentials
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Profile & Demographic Information
    name = Column(String, default="Eco Citizen")
    age = Column(Integer, default=20)
    gender = Column(String, default="Not Specified")
    city = Column(String, default="Default")
    household_size = Column(Integer, default=1)

    # Gamification Fields
    eco_points = Column(Integer, default=0)
    streak_count = Column(Integer, default=0)
    level = Column(Integer, default=1)
    tree_stage = Column(Integer, default=1)  # 1: Seedling, 2: Sprout, 3: Sapling, 4: Tree, 5: Forest

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # ORM Relationships
    assessments = relationship("AssessmentModel", back_populates="owner", cascade="all, delete-orphan")
    badges = relationship("UserBadgeModel", back_populates="owner", cascade="all, delete-orphan")
    bills = relationship("BillModel", back_populates="owner", cascade="all, delete-orphan")


class BillModel(Base):
    """
    Model for tracking utility bill file uploads for OCR/carbon analysis.
    """
    __tablename__ = "bills"

    # Primary Key & Foreign Key
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Bill Details
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    owner = relationship("UserModel", back_populates="bills")


class UserBadgeModel(Base):
    """
    Model for storing unlocked achievement badges per user.
    """
    __tablename__ = "user_badges"

    # Primary Key & Foreign Key
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Badge Details
    badge_name = Column(String, nullable=False)
    badge_description = Column(String, nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    owner = relationship("UserModel", back_populates="badges")


class AssessmentModel(Base):
    """
    Model for storing carbon footprint assessments calculated for users.
    """
    __tablename__ = "assessments"

    # Primary Key & Foreign Key
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Assessment Details
    date_str = Column(String, nullable=False)
    total_emissions = Column(Float, nullable=False)
    monthly_cost = Column(Float, nullable=False)
    is_zero_emission = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    owner = relationship("UserModel", back_populates="assessments")
