import re
import logging
from sqlalchemy.orm import Session
from system.db.db_service import SessionLocal
from system.db.models import Product # Assuming Product is your ORM model

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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
    logging.info(f"📦 Сохранение {len(products)} товаров в базу данных...")

    try:
        # ✅ Get all existing product links from the DB
        existing_links_result = db.query(Product.link).all()
        existing_links = set(r[0] for r in existing_links_result if r[0])  # Фильтруем None
        logging.info(f"📊 В базе данных уже есть {len(existing_links)} товаров")

        added_count = 0
        skipped_count = 0
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
            link = item.get("link", "").strip() if item.get("link") else None
            if not link or link in existing_links:
                skipped_count += 1
                continue
            existing_links.add(link)

            # Ensure images is a list
            images = item.get("images", [])
            if isinstance(images, str):
                images = [images]
            elif not isinstance(images, list):
                images = []

            # Create Product ORM object
            # Обработка цен: None если цена не указана, не 0
            sale_price = item.get("sale_price")
            first_price = item.get("first_price")
            
            # Если images пустой список, делаем None (для nullable поля)
            if not images:
                images = None
            
            product = Product(
                shop=item.get("shop", "Unknown"),
                name=item.get("name", "No Name"),
                images=images,
                link=link,
                brand=item.get("brand"),
                sale_price=sale_price,
                first_price=first_price,
                category=item.get("category", ["Обувь"]),
            )
            db.add(product)
            added_count += 1

        db.commit()
        logging.info(f"✅ Сохранено новых товаров: {added_count}")
        if skipped_count > 0:
            logging.info(f"⏭️  Пропущено дубликатов: {skipped_count}")
    except Exception as e:
        db.rollback()
        logging.error(f"❌ Ошибка сохранения в базу данных: {e}")
        import traceback
        traceback.print_exc()
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
