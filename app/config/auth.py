from datetime import datetime, timedelta
from fastapi import Depends, HTTPException,status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials,OAuth2PasswordBearer
from passlib.context import CryptContext
from argon2 import PasswordHasher
from dotenv import load_dotenv
from typing import List,Dict,Any,Optional
from jose import jwt,JWTError  
import secrets
import os
from datetime import datetime, timedelta


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

load_dotenv()
REFRESH_TOKEN_EXPIRE_DAYS = 3
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-jwt-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 200

pwd_context = PasswordHasher(
    time_cost=3,       
    memory_cost=65536, 
    parallelism=1,
    hash_len=32,
    salt_len=16
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify( hashed_password,plain_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return str(secrets.randbelow(1000000)).zfill(6)


def create_access_token(email: str, expires_delta: timedelta) -> str:
    """Create a JWT token with expiration"""
    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str ):#= Depends("oauth2_scheme")):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception