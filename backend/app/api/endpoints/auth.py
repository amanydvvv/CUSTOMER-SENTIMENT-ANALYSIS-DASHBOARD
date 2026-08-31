from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db, get_current_user, require_admin
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.models.user import User, UserRole
from backend.app.schemas.user import UserCreate, UserLogin, UserResponse, Token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """Register a new user account."""
    existing_user = db.query(User).filter(
        (User.email == user_in.email) | (User.username == user_in.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email or username already exists.",
        )

    # Sanitize role
    valid_roles = [r.value for r in UserRole]
    assigned_role = user_in.role.lower() if user_in.role.lower() in valid_roles else UserRole.VIEWER.value

    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name or user_in.username.capitalize(),
        hashed_password=get_password_hash(user_in.password),
        role=assigned_role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)) -> Any:
    """Authenticate user and return JWT access token."""
    user = db.query(User).filter(
        (User.email == login_data.username_or_email) | (User.username == login_data.username_or_email)
    ).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role,
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/login/oauth", response_model=Token)
def login_oauth(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Any:
    """OAuth2 compatible token login for Swagger UI."""
    return login(UserLogin(username_or_email=form_data.username, password=form_data.password), db=db)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> Any:
    """Fetch profile of currently authenticated user."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return current_user


@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """Admin-only: list registered users."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users
