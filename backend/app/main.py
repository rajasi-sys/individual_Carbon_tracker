"""
EcoQuest FastAPI Application Entry Point
----------------------------------------
Initializes the FastAPI app, configures CORS middleware, registers ORM models,
and automatically creates database tables upon server startup.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, profile, emissions, gamification

from app.database import Base, engine
import app.models  # Ensures all SQLAlchemy models are registered with Base metadata


# 1. Automatic Database Table Creation
# Provisions 'ecoquest.db' and all required tables defined in models.py upon startup.
Base.metadata.create_all(bind=engine)


# 2. FastAPI Application Instantiation
app = FastAPI(
    title="EcoQuest API",
    version="1.0.0",
    description="Backend API for EcoQuest Individual Carbon Footprint Tracker"
)
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(emissions.router)
app.include_router(gamification.router)

# 3. CORS (Cross-Origin Resource Sharing) Middleware Setup
# Enables cross-origin requests from web frontends (e.g. React, Vue, HTML/JS) to access the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 4. Root Health Check Endpoint
@app.get("/")
def read_root():
    """
    Health check endpoint to verify backend API server status.
    """
    return {"message": "EcoQuest API is running"}
