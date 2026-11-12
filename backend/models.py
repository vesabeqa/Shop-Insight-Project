from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    TIMESTAMP,
    UniqueConstraint,
    text,
    FetchedValue,
)
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey(
            "businesses.id",
            name="fk_users_business",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        )
    )
    full_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    role: Mapped[str] = mapped_column(
        ENUM("owner", "user"),
        server_default=text("'user'")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        UniqueConstraint("id", "business_id"),
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey(
            "businesses.id",
            name="fk_categories_business",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        )
    )
    name: Mapped[str] = mapped_column(String(100))

    __table_args__ = (
        UniqueConstraint("business_id", "name"),
        UniqueConstraint("id", "business_id"),
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(Integer)
    category_id: Mapped[int | None] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)

    purchase_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    selling_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    stock_quantity: Mapped[int] = mapped_column(
        Integer, server_default=text("0")
    )
    low_stock_threshold: Mapped[int] = mapped_column(
        Integer, server_default=text("5")
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=text("1")
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, server_onupdate=FetchedValue()
    )

    __table_args__ = (
        UniqueConstraint("id", "business_id"),

        ForeignKeyConstraint(
            ["business_id"],
            ["businesses.id"],
            name="fk_products_business",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),

        ForeignKeyConstraint(
            ["category_id", "business_id"],
            ["categories.id", "categories.business_id"],
            name="fk_products_category",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),

        CheckConstraint("purchase_price >= 0", name="chk_purchase_price"),
        CheckConstraint("selling_price >= 0", name="chk_selling_price"),
        CheckConstraint("stock_quantity >= 0", name="chk_stock_quantity"),
        CheckConstraint("low_stock_threshold >= 0", name="chk_low_stock"),
    )
