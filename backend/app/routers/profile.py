"""
EcoQuest Profile & Utility Bill Management Router
--------------------------------------------------
Endpoints for updating user profile demographics and uploading utility bill files for carbon tracking.
"""

import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserModel, BillModel
from app.schemas import ProfileUpdate
from app.security import get_current_user
from app.config import CITY_BENCHMARKS

router = APIRouter(prefix="/api/v1/user", tags=["Profile & Onboarding"])

# Ensure uploads directory exists on server startup
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/profile")
def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Updates the authenticated user's demographic profile and city baseline configuration.
    """
    current_user.name = profile_data.name
    current_user.age = profile_data.age
    current_user.gender = profile_data.gender

    # Validate city choice against available city benchmarks
    if profile_data.city in CITY_BENCHMARKS:
        current_user.city = profile_data.city
    else:
        current_user.city = "Default"

    current_user.household_size = profile_data.household_size

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully.",
        "city": current_user.city
    }


@router.post("/upload-bill")
def upload_utility_bill(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Uploads a utility bill image or PDF document to disk and registers the file in the database.
    """
    # Allowed file extensions for bill uploads
    allowed_extensions = (".png", ".jpg", ".jpeg", ".pdf")
    filename = file.filename or "uploaded_bill.png"
    ext = os.path.splitext(filename)[1].lower()

    if not ext or ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{ext}'. Allowed formats: .png, .jpg, .jpeg, .pdf"
        )

    # Sanitize and build unique destination path inside UPLOAD_DIR
    clean_filename = os.path.basename(filename)
    saved_filename = f"user_{current_user.id}_{clean_filename}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename).replace("\\", "/")

    # Write file content to disk
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save record in database
    new_bill = BillModel(
        user_id=current_user.id,
        file_path=saved_path
    )
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)

    return {
        "message": f"Bill '{file.filename}' uploaded successfully.",
        "file_path": saved_path
    }
