from __future__ import annotations

import re
from typing import List, Dict, Any, Optional

from sqlalchemy import func, and_, or_, select
from sqlalchemy.orm import Session

from system.db.models import Product

def _norm(text: str) -> str:
    s = (text or "").lower()
    s = re.sub(r"[^\w\s\-+]", " ", s, flags=re.U)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _tokens(text: str) -> List[str]:
    return [t for t in _norm(text).split() if len(t) >= 2]

def _fetch_distinct_categories(db: Session) -> list[str]:
    stmt = (
        select(func.distinct(func.lower(func.unnest(Product.category))).label("cat"))
        .where(Product.category.is_not(None))
    )
    result = db.execute(stmt).all()
    return [row[0] for row in result if row[0]]

def _fetch_distinct_brands(db: Session) -> list[str]:
    stmt = (
        select(func.distinct(func.lower(Product.brand)).label("brand"))
        .where(Product.brand.is_not(None))
        .where(Product.brand != "")
    )
    result = db.execute(stmt).all()
    return [row[0] for row in result if row[0]]

def search_products(
    db: Session, 
    q: str, 
    page: int = 1, 
    per_page: int = 28,
    sort: str = "relevance",
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> Dict[str, Any]:
    
    tokens = _tokens(q)
    
    if not tokens:
        return {
            "items": [], 
            "page": page, 
            "per_page": per_page, 
            "total": 0,
            "total_pages": 0
        }

    cat_set = set(_fetch_distinct_categories(db))
    
    normalized_query = _norm(q)
    shop_match = None
    shop_exists = db.execute(
        select(Product.shop)
        .where(Product.shop.is_not(None))
        .where(Product.shop != "")
        .where(func.lower(Product.shop) == normalized_query)
        .limit(1)
    ).first()
    if shop_exists:
        shop_match = shop_exists[0]
    
    brand_tokens_exact = []
    cat_tokens = []
    name_tokens = []
    
    if not shop_match:
        for t in tokens:
            if not t or len(t) < 2:
                continue
                
            exists = db.execute(
                select(Product.id)
                .where(Product.brand.is_not(None))
                .where(Product.brand != "")
                .where(Product.brand.ilike(f"%{t}%"))
                .limit(1)
            ).first()
            if exists:
                brand_tokens_exact.append(t)
            else:
                if t in cat_set:
                    cat_tokens.append(t)
                else:
                    name_tokens.append(t)

    q_sql = db.query(Product)

    if shop_match:
        q_sql = q_sql.filter(Product.shop == shop_match)
    else:
        if cat_tokens:
            q_sql = q_sql.filter(Product.category.overlap(cat_tokens))

        if brand_tokens_exact:
            brand_conds = [
                and_(
                    Product.brand.is_not(None),
                    Product.brand != "",
                    Product.brand.ilike(f"%{t}%")
                )
                for t in brand_tokens_exact
            ]
            q_sql = q_sql.filter(or_(*brand_conds))

        if name_tokens:
            name_conds = [
                and_(
                    Product.name.is_not(None),
                    Product.name != "",
                    Product.name.ilike(f"%{t}%")
                )
                for t in name_tokens
            ]
            q_sql = q_sql.filter(and_(*name_conds))

    if min_price is not None or max_price is not None:
        price_conditions = []
        
        if min_price is not None:
            price_conditions.append(
                or_(
                    Product.sale_price >= min_price,
                    and_(
                        Product.sale_price.is_(None),
                        Product.first_price >= min_price
                    )
                )
            )
        
        if max_price is not None:
            price_conditions.append(
                or_(
                    Product.sale_price <= max_price,
                    and_(
                        Product.sale_price.is_(None),
                        Product.first_price <= max_price
                    )
                )
            )
        
        if price_conditions:
            q_sql = q_sql.filter(and_(*price_conditions))

    if sort == "price_asc":
        q_sql = q_sql.order_by(
            Product.sale_price.asc().nulls_last(),
            Product.first_price.asc().nulls_last()
        )
    elif sort == "price_desc":
        q_sql = q_sql.order_by(
            Product.sale_price.desc().nulls_last(),
            Product.first_price.desc().nulls_last()
        )
    else:
        if cat_tokens:
            q_sql = q_sql.order_by(
                Product.sale_price.asc().nulls_last(),
                Product.first_price.asc().nulls_last()
            )
        else:
            q_sql = q_sql.order_by(Product.id.desc())

    total = q_sql.count()
    total_pages = (total + per_page - 1) // per_page

    offset = (page - 1) * per_page
    
    if page > total_pages and total_pages > 0:
        return {
            "items": [],
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        }
    
    rows = (
        q_sql.with_entities(
            Product.id,
            Product.name,
            Product.category,
            Product.brand,
            Product.sale_price,
            Product.first_price,
            Product.images,
            Product.link,
            Product.shop,
        )
        .offset(offset)
        .limit(per_page)
        .all()
    )

    items = [
        dict(
            id=r[0],
            name=r[1],
            category=r[2] or [],
            brand=r[3],
            sale_price=r[4],
            first_price=r[5],
            images=r[6] or [],
            link=r[7],
            shop=r[8],
        )
        for r in rows
    ]

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }
