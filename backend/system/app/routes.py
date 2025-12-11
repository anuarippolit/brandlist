# system/app/routes.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from system.db.db_service import get_db          # reuse your existing dependency
from system.app.search import search_products

router = APIRouter()

@router.get("/search")
def search(
    q: str = Query(..., min_length=1, description="User query in Russian"),
    page: int = Query(1, ge=1),
    per_page: int = Query(24, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return search_products(db, q=q, page=page, per_page=per_page)
