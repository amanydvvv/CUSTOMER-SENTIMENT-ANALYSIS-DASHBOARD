from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.db.session import SessionLocal
from backend.app.core.security import decode_access_token
from backend.app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    """Retrieve current user from JWT token."""
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username_or_id = payload.get("sub")
    if not username_or_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload invalid",
        )

    user = None
    if str(username_or_id).isdigit():
        user = db.query(User).filter(User.id == int(username_or_id)).first()
    if not user:
        user = db.query(User).filter(
            (User.username == str(username_or_id)) | (User.email == str(username_or_id))
        ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    return user


class RoleChecker:
    """RBAC dependency to enforce permitted roles on endpoints."""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = [r.lower() for r in allowed_roles]

    def __call__(self, current_user: Optional[User] = Depends(get_current_user)) -> User:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials required",
            )

        if current_user.role.lower() not in self.allowed_roles and current_user.role.lower() != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: Role '{current_user.role}' lacks permission. Required: {self.allowed_roles}",
            )
        return current_user


# Convenience role dependencies
require_admin = RoleChecker(["admin"])
require_analyst = RoleChecker(["admin", "analyst"])
require_viewer = RoleChecker(["admin", "analyst", "viewer"])
