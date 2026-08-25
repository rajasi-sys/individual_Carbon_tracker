"""
EcoQuest Database Configuration & Connection Setup
--------------------------------------------------
Configures the SQLAlchemy ORM engine, session factory, declarative base,
and database dependency generator for FastAPI request handling.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# 1. Database URL & Engine Setup
# SQLite database file named 'ecoquest.db' stored in the root folder of the backend project.
SQLALCHEMY_DATABASE_URL = "sqlite:///./ecoquest.db"

# Create the SQLAlchemy engine instance.
# 'connect_args={"check_same_thread": False}' allows SQLite to handle multiple concurrent threads in FastAPI.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 2. Session & Base Declarations
# SessionLocal is a factory for database sessions, bound to our engine.
# autocommit=False ensures transactions require explicit commit operations.
# autoflush=False prevents automatic flushing of pending changes before database queries.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for defining database models. All ORM models will inherit from Base.
Base = declarative_base()


# 3. Database Dependency Generator
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency generator function.
    Creates a new database session for an incoming HTTP request and yields it
    to the endpoint handler. Automatically ensures the session is closed when
    the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Safely close the database session in the finally block
        db.close()
