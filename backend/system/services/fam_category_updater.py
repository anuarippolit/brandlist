import os
import json
from sqlalchemy import create_engine, text
from system.config import settings
from system.db.models import Product
from system.db.db_service import SessionLocal

# Path to filters.json
FILTERS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "filters.json")

def ensure_column():
    """Add fam_category column if not exists"""
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text(
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS fam_category VARCHAR(255);"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_products_fam_category ON products(fam_category);"
        ))
        conn.commit()
    print("✅ Column fam_category ensured")

def load_mapping():
    with open(FILTERS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("category_mapping", {})

def resolve_fam(categories, mapping):
    if not categories:
        return None
    for c in categories:
        fam = mapping.get(c)
        if fam:
            return fam
    return None

def backfill():
    """Fill fam_category for existing products"""
    mapping = load_mapping()
    db = SessionLocal()
    updated = 0
    try:
        products = db.query(Product).all()
        for p in products:
            fam = resolve_fam(p.category, mapping)
            if fam and p.fam_category != fam:
                p.fam_category = fam
                updated += 1
        db.commit()
        print(f"✅ Updated {updated} rows")
    except Exception as e:
        db.rollback()
        print("❌ Error:", e)
    finally:
        db.close()

if __name__ == "__main__":
    ensure_column()
    backfill()
