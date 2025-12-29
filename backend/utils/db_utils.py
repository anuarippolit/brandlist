import re
import logging
from sqlalchemy.orm import Session
from system.db.db_service import SessionLocal
from system.db.models import Product

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
        existing_links_result = db.query(Product.link).all()
        existing_links = set(r[0] for r in existing_links_result if r[0])
        logging.info(f"📊 В базе данных уже есть {len(existing_links)} товаров")

        added_count = 0
        skipped_count = 0
        for item in products:
            item["sale_price"] = parse_price(item.get("sale_price"))
            item["first_price"] = parse_price(item.get("first_price"))
            category = item.get("category")
            if isinstance(category, str):
                item["category"] = [category]
            elif not isinstance(category, list):
                item["category"] = []

            link = item.get("link", "").strip() if item.get("link") else None
            if not link or link in existing_links:
                skipped_count += 1
                continue
            existing_links.add(link)

            images = item.get("images", [])
            if isinstance(images, str):
                images = [images]
            elif not isinstance(images, list):
                images = []

            sale_price = item.get("sale_price")
            first_price = item.get("first_price")
            
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
