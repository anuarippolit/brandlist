# system/app/routes.py
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session

from system.db.db_service import get_db
from system.app.search import search_products
from system.app.schemas import SearchResponse, ProductResponse
from system.app.security import (
    limiter,
    SEARCH_RATE_LIMIT,
    PRODUCT_RATE_LIMIT,
    BATCH_PRODUCTS_RATE_LIMIT
)
from system.db.models import Product

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
@limiter.limit(SEARCH_RATE_LIMIT)
async def search(
    request: Request,
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1, le=1000),
    per_page: int = Query(28, ge=1, le=28),
    sort: str = Query("relevance", regex="^(relevance|price_asc|price_desc)$"),
    min_price: float = Query(None, ge=0, le=10000000),
    max_price: float = Query(None, ge=0, le=10000000),
    db: Session = Depends(get_db),
):
    """Поиск товаров с фильтрами и сортировкой"""
    try:
        # Валидация max_price >= min_price
        if max_price is not None and min_price is not None:
            if max_price < min_price:
                raise HTTPException(
                    status_code=400,
                    detail="max_price must be >= min_price"
                )

        result = search_products(
            db=db,
            q=q,
            page=page,
            per_page=per_page,
            sort=sort,
            min_price=min_price,
            max_price=max_price,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/products/{product_id}", response_model=ProductResponse)
@limiter.limit(PRODUCT_RATE_LIMIT)
async def get_product(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
):
    """Получить товар по ID"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return ProductResponse(
            id=product.id,
            name=product.name,
            brand=product.brand,
            category=product.category or [],
            sale_price=product.sale_price,
            first_price=product.first_price,
            images=product.images or [],
            link=product.link,
            shop=product.shop,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/products", response_model=list[ProductResponse])
@limiter.limit(BATCH_PRODUCTS_RATE_LIMIT)
async def get_products_by_ids(
    request: Request,
    ids: str = Query(..., regex=r'^\d+(,\d+)*$', max_length=500),
    db: Session = Depends(get_db),
):
    """Получить товары по списку ID (для favorites)"""
    try:
        # Парсим IDs
        id_list = [
            int(id_str.strip())
            for id_str in ids.split(',')
            if id_str.strip().isdigit()
        ]

        # Максимум 50 ID за запрос
        if len(id_list) > 50:
            id_list = id_list[:50]

        if not id_list:
            return []

        products = db.query(Product).filter(Product.id.in_(id_list)).all()

        return [
            ProductResponse(
                id=p.id,
                name=p.name,
                brand=p.brand,
                category=p.category or [],
                sale_price=p.sale_price,
                first_price=p.first_price,
                images=p.images or [],
                link=p.link,
                shop=p.shop,
            )
            for p in products
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
