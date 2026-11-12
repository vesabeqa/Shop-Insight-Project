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

class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), server_default=text("0")
    )
    sale_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        UniqueConstraint("id", "business_id"),
        Index("idx_sales_business_date", "business_id", "sale_date"),

        ForeignKeyConstraint(
            ["business_id"],
            ["businesses.id"],
            name="fk_sales_business",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),

        ForeignKeyConstraint(
            ["user_id", "business_id"],
            ["users.id", "users.business_id"],
            name="fk_sales_user",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),

        CheckConstraint("total_amount >= 0", name="chk_total_amount"),
    )


 
class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(Integer)
    sale_id: Mapped[int] = mapped_column(Integer)
    product_id: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)

    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    __table_args__ = (
        UniqueConstraint("sale_id", "product_id"),

        ForeignKeyConstraint(
            ["sale_id", "business_id"],
            ["sales.id", "sales.business_id"],
            name="fk_sale_items_sale",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),

        ForeignKeyConstraint(
            ["product_id", "business_id"],
            ["products.id", "products.business_id"],
            name="fk_sale_items_product",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),

        CheckConstraint("quantity > 0", name="chk_sale_quantity"),
        CheckConstraint("unit_price >= 0", name="chk_unit_price"),
        CheckConstraint("unit_cost >= 0", name="chk_unit_cost"),
    )



class StockAlert(Base):
    __tablename__ = "stock_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(Integer)
    product_id: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(String(255))

    is_resolved: Mapped[bool] = mapped_column(
        Boolean, server_default=text("0")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        Index("idx_stock_alerts_resolved", "business_id", "is_resolved"),

        ForeignKeyConstraint(
            ["product_id", "business_id"],
            ["products.id", "products.business_id"],
            name="fk_stock_alerts_product",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )



class ImportLog(Base):
    __tablename__ = "import_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    file_name: Mapped[str] = mapped_column(String(255))

    total_rows: Mapped[int] = mapped_column(
        Integer, server_default=text("0")
    )
    successful_rows: Mapped[int] = mapped_column(
        Integer, server_default=text("0")
    )
    rejected_rows: Mapped[int] = mapped_column(
        Integer, server_default=text("0")
    )

    error_details: Mapped[str | None] = mapped_column(Text)
    imported_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        Index("idx_import_logs_business_date", "business_id", "imported_at"),

        ForeignKeyConstraint(
            ["business_id"],
            ["businesses.id"],
            name="fk_import_logs_business",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),

        ForeignKeyConstraint(
            ["user_id", "business_id"],
            ["users.id", "users.business_id"],
            name="fk_import_logs_user",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),

        CheckConstraint("total_rows >= 0", name="chk_total_rows"),
        CheckConstraint("successful_rows >= 0", name="chk_successful_rows"),
        CheckConstraint("rejected_rows >= 0", name="chk_rejected_rows"),
    )



class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(String(100), unique=True)
    business_id: Mapped[int] = mapped_column(Integer)
    sale_id: Mapped[int] = mapped_column(Integer)

    processed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["sale_id", "business_id"],
            ["sales.id", "sales.business_id"],
            name="fk_processed_events_sale",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )
