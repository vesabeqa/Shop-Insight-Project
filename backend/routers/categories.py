
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user, require_owner
from backend.models import Category, Product, User
from backend.schemas import CategoryCreate, CategoryUpdate, CategoryOut


router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    data: CategoryCreate,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    category = Category(
        business_id=owner.business_id,
        name=data.name,
    )

    db.add(category)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists",
        )

    db.refresh(category)
    return category


@router.get("", response_model=list[CategoryOut])
def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    categories = db.scalars(
        select(Category).where(
            Category.business_id == current_user.business_id
        )
    ).all()

    return categories


def get_category_or_404(
    db: Session,
    business_id: int,
    category_id: int,
):
    category = db.scalar(
        select(Category).where(
            Category.id == category_id,
            Category.business_id == business_id,
        )
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return category


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_category_or_404(
        db,
        current_user.business_id,
        category_id,
    )


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    category = get_category_or_404(
        db,
        owner.business_id,
        category_id,
    )

    updates = data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    if updates.get("name") is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Category name cannot be null",
        )

    category.name = updates["name"]

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists",
        )

    db.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    category = get_category_or_404(
        db,
        owner.business_id,
        category_id,
    )

    product_exists = db.scalar(
        select(Product.id).where(
            Product.category_id == category_id,
            Product.business_id == owner.business_id,
        ).limit(1)
    )

    if product_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete category because it is used by products",
        )

    db.delete(category)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category cannot be deleted because it is in use",
        )

    return {"message": "Category deleted successfully"}
