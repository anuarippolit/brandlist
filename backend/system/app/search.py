# system/app/search.py
from __future__ import annotations

import re
from typing import List, Dict, Any

from sqlalchemy import func, and_, or_, select
from sqlalchemy.orm import Session

from system.db.models import Product


# ----------------- utils -----------------

def _norm(text: str) -> str:
    s = (text or "").lower()
    s = re.sub(r"[^\w\s\-+]", " ", s, flags=re.U)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _tokens(text: str) -> List[str]:
    return [t for t in _norm(text).split() if len(t) >= 2]

def _name_expr():
    # unaccent + lower for tolerant matches
    return func.unaccent(func.lower(Product.name))

def _brand_expr():
    return func.unaccent(func.lower(Product.brand))

def _cat_text_expr():
    # string view of the category array (for debugging or optional LIKE filters)
    return func.coalesce(func.array_to_string(Product.category, " "), "")

# ----------------- dictionaries from DB -----------------

def _fetch_distinct_categories(db: Session) -> list[str]:
    # SELECT DISTINCT lower(unnest(category)) FROM products WHERE category IS NOT NULL;
    stmt = (
        select(func.distinct(func.lower(func.unnest(Product.category))).label("cat"))
        .where(Product.category.is_not(None))
    )
    return [row[0] for row in db.execute(stmt).all()]

def _fetch_distinct_brands(db: Session) -> list[str]:
    # SELECT DISTINCT lower(brand) FROM products WHERE brand IS NOT NULL;
    stmt = (
        select(func.distinct(func.lower(Product.brand)).label("brand"))
        .where(Product.brand.is_not(None))
    )
    return [row[0] for row in db.execute(stmt).all()]

# ----------------- core search -----------------

def search_products(db: Session, q: str, page: int = 1, per_page: int = 24) -> Dict[str, Any]:
    tokens = _tokens(q)
    if not tokens:
        return {"items": [], "page": page, "per_page": per_page, "total": 0, "meta": {"detected": {}}}

    # 1) Detect categories and (exact) brands from DB dictionaries
    cat_set = set(_fetch_distinct_categories(db))
    brand_set = set(_fetch_distinct_brands(db))

    cat_tokens = [t for t in tokens if t in cat_set]
    brand_tokens_exact = [t for t in tokens if t in brand_set]
    other_tokens = [t for t in tokens if t not in cat_set]  # candidates for brand or name

    q_sql = db.query(Product)

    # 2) Category-first filter (exact overlap with array values)
    if cat_tokens:
        # translates to: product.category && ARRAY[:cat_tokens]
        q_sql = q_sql.filter(Product.category.overlap(cat_tokens))

    # 3) Brand filter
    tokens_for_brand: List[str] = brand_tokens_exact[:]

    if not tokens_for_brand:
        # Guarded fuzzy: only treat a token as brand if at least one row matches ILIKE
        valid = []
        for t in other_tokens:
            pattern = f"%{t}%"
            exists = db.execute(
                select(Product.id).where(Product.brand.ilike(pattern)).limit(1)
            ).first()
            if exists:
                valid.append(t)
        tokens_for_brand = valid

    if tokens_for_brand:
        brand = _brand_expr()
        # fuzzy brand: ILIKE OR trigram similarity
        brand_conds = [or_(brand.ilike(f"%{t}%"), func.similarity(brand, t) >= 0.4) for t in tokens_for_brand]
        q_sql = q_sql.filter(or_(*brand_conds))

    # 4) Name fallback (only if user didn't hit a category)
    if not cat_tokens:
        name = _name_expr()
        # AND all tokens in name for a precise fallback
        name_conds = [name.ilike(f"%{t}%") for t in tokens]
        q_sql = q_sql.filter(and_(*name_conds))

    # 5) Sorting
    if cat_tokens:
        # When user asked a category, cheaper first feels right
        q_sql = q_sql.order_by(
            Product.sale_price.asc().nulls_last(),
            Product.first_price.asc().nulls_last(),
        )
    else:
        # Name/brand only: show newest-ish
        q_sql = q_sql.order_by(Product.id.desc())

    # 6) Pagination + projection
    total = q_sql.count()
    rows = (
        q_sql.with_entities(
            Product.id,
            Product.name,
            Product.fam_category,
            Product.category,
            Product.brand,
            Product.sale_price,
            Product.first_price,
        )
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    items = [
        dict(
            id=r[0],
            name=r[1],
            fam_category=r[2],
            category=r[3],
            brand=r[4],
            sale_price=r[5],
            first_price=r[6],
        )
        for r in rows
    ]

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "meta": {
            "mode": "category-first" if cat_tokens else "name-first",
            "detected": {
                "category_tokens": cat_tokens,
                "brand_tokens": tokens_for_brand,
                "name_tokens": [] if cat_tokens else tokens,
            },
        },
    }
