from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user, require_owner
from backend.models import Business, User
from backend.schemas import (
    CreateUserRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from backend.security import (
    DUMMY_HASH,
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

EMAIL_TAKEN = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Email is already registered",
)


def _email_exists(db: Session, email: str) -> bool:
    return db.scalar(select(User.id).where(User.email == email)) is not None


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new business together with its owner account."""
    email = data.email.lower()
    if _email_exists(db, email):
        raise EMAIL_TAKEN

    business = Business(name=data.business_name)
    db.add(business)
    db.flush()  

    user = User(
        business_id=business.id,
        full_name=data.full_name,
        email=email,
        password_hash=hash_password(data.password),
        role="owner",
    )
    db.add(user)

    try:
        db.commit()  
    except IntegrityError:
        db.rollback()
        raise EMAIL_TAKEN

    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Log in with email (the 'username' field) and password."""
    email = form.username.strip().lower()
    user = db.scalar(select(User).where(User.email == email))

    password_ok = verify_password(
        form.password,
        user.password_hash if user else DUMMY_HASH,
    )
    if user is None or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.id, user.business_id, user.role)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_employee(
    data: CreateUserRequest,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    """Owner-only: add an employee (role 'user') to the owner's business."""
    email = data.email.lower()
    if _email_exists(db, email):
        raise EMAIL_TAKEN

    user = User(
        business_id=owner.business_id,
        full_name=data.full_name,
        email=email,
        password_hash=hash_password(data.password),
        role="user",
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EMAIL_TAKEN

    db.refresh(user)
    return user