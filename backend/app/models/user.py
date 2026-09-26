from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.app.db.base import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default=UserRole.VIEWER.value, nullable=False)
    is_active = Column(Boolean(), default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
