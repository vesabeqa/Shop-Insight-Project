
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user, require_owner
from backend.models import Category, Product, User
from backend.schemas import ProductCreate, ProductUpdate, ProductOut


router = APIRouter(prefix="/products", tags=["products"])


def get_product_or_404(db: Session, business_id: int, product_id: int):
    product = db.scalar(
        select(Product).where(
            Product.id == product_id,
            Product.business_id == business_id,
            Product.is_active.is_(True),
        )
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


def check_category(db: Session, business_id: int, category_id: int | None):
    if category_id is None:
        return

    category = db.scalar(
        select(Category).where(
            Category.id == category_id,
            Category.business_id == business_id,
        )
    )

    if category is None:
        raise HTTPException(
            status_code=400,
            detail="Category not found in your business",
        )


@router.post(
    "",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    data: ProductCreate,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    check_category(db, owner.business_id, data.category_id)

    product = Product(
        business_id=owner.business_id,
        **data.model_dump(),
    )

    db.add(product)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not create product",
        )

    db.refresh(product)
    return product


@router.get("", response_model=list[ProductOut])
def list_products(
    search: str | None = Query(default=None, max_length=100),
    category_id: int | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(Product).where(
        Product.business_id == current_user.business_id,
        Product.is_active.is_(True),
    )
    if search:
        query = query.where(Product.name.contains(search, autoescape=True))
    if category_id is not None:
        query = query.where(Product.category_id == category_id)

    query = query.order_by(Product.name, Product.id).limit(limit).offset(offset)
    return db.scalars(query).all()

    return products


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_product_or_404(
        db, current_user.business_id, product_id
    )


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    product = get_product_or_404(
        db, owner.business_id, product_id
    )

    updates = data.model_dump(exclude_unset=True)

    required_fields = {
        "name",
        "purchase_price",
        "selling_price",
        "stock_quantity",
        "low_stock_threshold",
    }

    for field in required_fields:
        if field in updates and updates[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null",
            )

    if "category_id" in updates:
        check_category(
            db, owner.business_id, updates["category_id"]
        )

    for field, value in updates.items():
        setattr(product, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not update product",
        )

    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    product = get_product_or_404(
        db, owner.business_id, product_id
    )

    product.is_active = False
    db.commit()

    return {"message": "Product deactivated successfully"}
