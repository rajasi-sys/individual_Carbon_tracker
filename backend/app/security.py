"""
EcoQuest Security & Authentication Handler
------------------------------------------
Provides password hashing/verification using PassLib (bcrypt), JWT access token
generation/decoding using Python-Jose, and FastAPI current user validation dependency.
"""

from datetime import datetime, timedelta
from typing import Optional
import bcrypt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db
from app.models import UserModel


# 1. Password Hashing Configuration
# CryptContext using bcrypt scheme for password hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored bcrypt hash.
    Falls back to direct bcrypt verification if passlib encounters version incompatibilities.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """
    Returns a secure bcrypt hash of the provided plain-text password.
    Falls back to direct bcrypt hashing if passlib encounters version incompatibilities.
    """
    try:
        return pwd_context.hash(password)
    except Exception:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# 2. JWT Token Creation & OAuth2 Bearer Scheme
# Specifies the login endpoint path for obtaining OAuth2 Bearer JWT tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Encodes payload data into a signed JWT access token.

    Args:
        data (dict): Data payload to embed in token (e.g. {"sub": user.email}).
        expires_delta (Optional[timedelta]): Custom token expiration duration.

    Returns:
        str: Encoded JWT token string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 3. Authentication & Current User Validation Dependency
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    """
    FastAPI dependency that decodes the incoming JWT token from the Authorization header,
    extracts the user email ('sub' claim), and queries the database for the active UserModel.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token using system SECRET_KEY and ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Retrieve user from database
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if user is None:
        raise credentials_exception

    return user
