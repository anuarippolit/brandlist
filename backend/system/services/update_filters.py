import json
import os
from system.db.models import Product
from system.db.db_service import SessionLocal

# Путь к filters.json
FILTERS_PATH = os.path.join("system", "data", "filters.json")

def update_filters_json():
    session = SessionLocal()
    try:
        # Загружаем текущие фильтры
        try:
            with open(FILTERS_PATH, "r", encoding="utf-8") as f:
                filters = json.load(f)
        except FileNotFoundError:
            filters = {}

        # Собираем уникальные бренды и категории из БД
        all_products = session.query(Product).all()
        brands = set()
        categories = set()

        for product in all_products:
            if product.brand:
                brands.add(product.brand.strip())
            if product.category:
                categories.update([c.strip() for c in product.category])

        colors = set()
        for product in all_products:
            if product.colors:
                colors.update([c.strip() for c in product.colors])
        filters["color"] = sorted(colors)

        # Обновляем содержимое
        filters["brand"] = sorted(brands)
        filters["category"] = sorted(categories)

        with open(FILTERS_PATH, "w", encoding="utf-8") as f:
            json.dump(filters, f, indent=2, ensure_ascii=False)

        print("✅ filters.json успешно обновлён!")
    finally:
        session.close()

if __name__ == "__main__":
    update_filters_json()
