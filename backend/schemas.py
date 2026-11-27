from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class CreateUserRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        # bcrypt accepts a maximum of 72 bytes
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes long")
        return value


class RegisterRequest(CreateUserRequest):
    business_name: str = Field(min_length=2, max_length=150)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    full_name: str
    email: EmailStr
    role: str
    created_at: datetime | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut



class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    category_id: int | None = None
    purchase_price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    selling_price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    stock_quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    category_id: int | None = None
    purchase_price: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    selling_price: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    stock_quantity: int | None = Field(default=None, ge=0)
    low_stock_threshold: int | None = Field(default=None, ge=0)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    category_id: int | None
    name: str
    description: str | None
    purchase_price: Decimal
    selling_price: Decimal
    stock_quantity: int
    low_stock_threshold: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    
class CategoryCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    name: str
