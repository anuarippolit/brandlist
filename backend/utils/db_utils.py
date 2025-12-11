import re
from sqlalchemy.orm import Session
from system.db.db_service import SessionLocal
from system.db.models import Product # Assuming Product is your ORM model

def parse_price(value):
    """
    Parses a price string to float. Cleans currency symbols, spaces, commas, etc.
    """
    if isinstance(value, (int, float)):
        return float(value)
    if not value or not isinstance(value, str):
        return None
    cleaned = re.sub(r"[^\d.,]", "", value).replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None

def save_products_to_db(products):
    """
    Saves a list of product dictionaries into the PostgreSQL database,
    skipping products with duplicate links.
    """
    db: Session = SessionLocal()
    print(f"📦 Saving {len(products)} products into the database...")

    try:
        # ✅ Get all existing product links from the DB
        existing_links = set(r[0] for r in db.query(Product.link).all())

        added_count = 0
        for item in products:
            # Parse and clean price fields
            item["sale_price"] = parse_price(item.get("sale_price"))
            item["first_price"] = parse_price(item.get("first_price"))

            # Ensure 'category' field is a list
            category = item.get("category")
            if isinstance(category, str):
                item["category"] = [category]
            elif not isinstance(category, list):
                item["category"] = []

            # 🧱 Skip if link already exists
            if item.get("link") in existing_links:
                continue
            existing_links.add(item["link"])

            # Create Product ORM object
            product = Product(
                shop=item.get("shop", "Unknown"),
                name=item.get("name", "No Name"),
                color=item.get("color", "Unknown Color"),
                image_url=item.get("image_url", ""),
                link=item.get("link", ""),
                sizes=item.get("sizes", []),
                brand=item.get("brand", "Unknown Brand"),
                sale_price=item.get("sale_price", 0),
                first_price=item.get("first_price", 0),
                category=item.get("category", []),
            )
            db.add(product)
            added_count += 1

        db.commit()
        print(f"✅ {added_count} new products saved to DB.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error saving to database: {e}")
    finally:
        db.close()

# def save_products_to_db(products):
#     """
#     Saves a list of product dictionaries into the PostgreSQL database.
#     """
#     db: Session = SessionLocal()
#
#     print(f"📦 Saving {len(products)} products into the database...")
#
#     try:
#         for item in products:
#             # Parse and clean price fields
#             item["sale_price"] = parse_price(item.get("sale_price"))
#             item["first_price"] = parse_price(item.get("first_price"))
#
#             # Ensure 'category' field is a list
#             category = item.get("category")
#             if isinstance(category, str):
#                 item["category"] = [category]
#             elif not isinstance(category, list):
#                 item["category"] = []
#
#             # Create Product ORM object
#             product = Product(
#                 shop=item.get("shop", "Unknown"),
#                 name=item.get("name", "No Name"),
#                 color=item.get("color", "Unknown Color"),
#                 image_url=item.get("image_url", ""),
#                 link=item.get("link", ""),
#                 sizes=item.get("sizes", []),
#                 brand=item.get("brand", "Unknown Brand"),
#                 sale_price=item.get("sale_price", 0),
#                 first_price=item.get("first_price", 0),
#                 category=item.get("category", []),
#             )
#
#             db.add(product)
#
#         db.commit()
#         print("✅ Products successfully saved into DB!")
#     except Exception as e:
#         db.rollback()
#         print(f"❌ Error saving to database: {e}")
#     finally:
#         db.close()
