from database import SessionLocal
from models import FurnitureProduct


db = SessionLocal()


products = [
    FurnitureProduct(
        name="Modern Wooden Chair",
        category="chair",
        price=4999,
        image_filename="chair_1.jpg"
    ),
    FurnitureProduct(
        name="Comfort Office Chair",
        category="chair",
        price=6999,
        image_filename="chair_2.jpeg"
    ),
    FurnitureProduct(
        name="Wooden Dining Table",
        category="table",
        price=12999,
        image_filename="table_1.jpeg"
    ),
    FurnitureProduct(
        name="Modern Study Table",
        category="table",
        price=8999,
        image_filename="table_2.jpeg"
    ),
    FurnitureProduct(
        name="King Size Bed",
        category="bed",
        price=19999,
        image_filename="bed_1.jpeg"
    )
]


db.add_all(products)

db.commit()

db.close()

print("Furniture products added successfully!")