"""
Seed the database with demo data.
Run:  docker compose exec backend python -m backend.seed
"""
from decimal import Decimal

from sqlalchemy import select

from backend.database import SessionLocal
from backend.models import Business, Category, Product, User
from backend.security import hash_password

OWNER_EMAIL = "demo.owner@shopinsight.com"
EMPLOYEE_EMAIL = "demo.employee@shopinsight.com"
PASSWORD = "Password123"

# category -> (name, purchase price, selling price, stock, low-stock threshold)
CATALOG = {
    "Drinks": [
        ("Cola 0.5L", "0.40", "1.00", 120, 20),
        ("Orange Juice 1L", "0.90", "1.80", 45, 10),
        ("Mineral Water 1.5L", "0.20", "0.60", 200, 30),
        ("Energy Drink 0.25L", "0.70", "1.50", 8, 15),
    ],
    "Snacks": [
        ("Potato Chips 150g", "0.80", "1.70", 60, 15),
        ("Chocolate Bar", "0.50", "1.10", 90, 20),
        ("Salted Peanuts 200g", "0.90", "1.90", 5, 5),
        ("Biscuits 300g", "0.60", "1.40", 70, 15),
    ],
    "Dairy": [
        ("Milk 1L", "0.70", "1.20", 4, 10),
        ("Yogurt 250g", "0.30", "0.70", 80, 20),
        ("White Cheese 400g", "2.20", "3.80", 25, 8),
        ("Butter 200g", "1.40", "2.40", 30, 10),
    ],
    "Bakery": [
        ("White Bread", "0.30", "0.60", 3, 8),
        ("Croissant", "0.25", "0.80", 40, 10),
        ("Whole Wheat Bread", "0.45", "0.90", 20, 8),
    ],
    "Household": [
        ("Dish Soap 500ml", "1.10", "2.20", 35, 10),
        ("Paper Towels 2pk", "1.30", "2.50", 50, 12),
        ("Laundry Detergent 2L", "4.50", "7.90", 18, 6),
    ],
}


def main() -> None:
    with SessionLocal() as db:
        if db.scalar(select(User.id).where(User.email == OWNER_EMAIL)):
            print("Demo data already exists. Nothing to do.")
            return

        business = Business(name="Demo Market")
        db.add(business)
        db.flush()

        password_hash = hash_password(PASSWORD)
        db.add(User(
            business_id=business.id,
            full_name="Demo Owner",
            email=OWNER_EMAIL,
            password_hash=password_hash,
            role="owner",
        ))
        db.add(User(
            business_id=business.id,
            full_name="Demo Employee",
            email=EMPLOYEE_EMAIL,
            password_hash=password_hash,
            role="user",
        ))

        products_count = 0
        for category_name, items in CATALOG.items():
            category = Category(business_id=business.id, name=category_name)
            db.add(category)
            db.flush()
            for name, buy, sell, stock, threshold in items:
                db.add(Product(
                    business_id=business.id,
                    category_id=category.id,
                    name=name,
                    purchase_price=Decimal(buy),
                    selling_price=Decimal(sell),
                    stock_quantity=stock,
                    low_stock_threshold=threshold,
                ))
                products_count += 1

        db.commit()
        print(f"Created business 'Demo Market' with {len(CATALOG)} categories "
              f"and {products_count} products.")
        print(f"Owner:    {OWNER_EMAIL} / {PASSWORD}")
        print(f"Employee: {EMPLOYEE_EMAIL} / {PASSWORD}")


if __name__ == "__main__":
    main()

    """
    Boneni:
    docker compose restart backend
    docker compose logs -f backend
    Pritet Application startup complete.
    docker compose exec backend python -m backend.seed 
    Pritet mesazhi Created business 'Demo Market' with 5 categories and 18 products.
    Owner:    demo.owner@shopinsight.com / Password123
    Employee: demo.employee@shopinsight.com / Password123
    """