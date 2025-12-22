from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal


class ProductResponse(BaseModel):
    id: int
    name: str
    brand: Optional[str]
    category: List[str]
    sale_price: Optional[float]
    first_price: Optional[float]
    images: List[str]
    link: Optional[str]
    shop: str

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    items: List[ProductResponse]
    page: int
    per_page: int
    total: int
    total_pages: int

