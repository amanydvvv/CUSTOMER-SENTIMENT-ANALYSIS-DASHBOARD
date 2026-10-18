"""
auth.py
───────
JWT Authentication + Role-Based Access Control (RBAC).

Architecture: Security Layer (Planned for Review-3) as per project presentation.

Roles:
  - viewer  : Can read all GET endpoints (stats, reviews, models)
  - analyst : Can also call POST /predict and POST /predict/batch

Endpoints:
  POST /auth/register  — create a new user account
  POST /auth/login     — returns a signed JWT access token
  GET  /auth/me        — returns current user info (requires token)
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.db import models as db_models

# ── JWT config ────────────────────────────────────────────────────────────────
SECRET_KEY  = os.getenv("JWT_SECRET_KEY", "sentiment-dashboard-secret-key-review3-2026")
ALGORITHM   = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 8   # 8 hours

# ── FastAPI setup ─────────────────────────────────────────────────────────────
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# ── Pydantic schemas ──────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    username: str
    password: str
    role: Optional[str] = "viewer"   # default role


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str


class UserInfo(BaseModel):
    username: str
    role: str


# ── Password hashing (native bcrypt) ──────────────────────────────────────────
import bcrypt


def hash_password(password: str) -> str:
    # Truncate to 72 bytes as per bcrypt specification
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    try:
        plain_bytes = plain.encode('utf-8')[:72]
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False


# ── JWT creation / decoding ───────────────────────────────────────────────────
from jose import JWTError, jwt


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# ── Dependency: get current user from token ───────────────────────────────────
def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[db_models.User]:
    """Returns current user or None (for optional auth on public endpoints)."""
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    username = payload.get("sub")
    if not username:
        return None
    return db.query(db_models.User).filter(db_models.User.username == username).first()


def require_analyst(current_user: Optional[db_models.User] = Depends(get_current_user)):
    """Dependency that enforces analyst role. Raises 401/403 if not authenticated."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user.role not in ("analyst", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Analyst role required. Your role: {current_user.role}",
        )
    return current_user


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("/register", response_model=UserInfo, status_code=201)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user. Default role is 'viewer'."""
    existing = db.query(db_models.User).filter(
        db_models.User.username == user_data.username
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken.")

    allowed_roles = ("viewer", "analyst")
    role = user_data.role if user_data.role in allowed_roles else "viewer"

    new_user = db_models.User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        role=role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserInfo(username=new_user.username, role=new_user.role)


@router.post("/login", response_model=Token)
def login(login_req: UserLogin, db: Session = Depends(get_db)):
    """Login with JSON payload and receive a JWT access token."""
    user = db.query(db_models.User).filter(
        db_models.User.username == login_req.username
    ).first()
    if not user or not verify_password(login_req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user.username, "role": user.role})
    return Token(
        access_token=token,
        token_type="bearer",
        username=user.username,
        role=user.role,
    )


@router.get("/me", response_model=UserInfo)
def get_me(current_user: db_models.User = Depends(get_current_user)):
    """Return the currently authenticated user's info (all roles)."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserInfo(username=current_user.username, role=current_user.role)
