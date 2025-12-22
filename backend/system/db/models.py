from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    shop = Column(String, nullable=False)
    name = Column(String, nullable=False)

    # Массивы
    images = Column(ARRAY(String), nullable=True)  # List of image URLs
    category = Column(ARRAY(String), nullable=True)  # List of categories (e.g., ["Обувь", "Кроссовки"])

    # Основные поля
    link = Column(String, nullable=True, unique=True, index=True)  # Product page URL (unique для избежания дубликатов)
    brand = Column(String, nullable=True, index=True)  # Brand name
    sale_price = Column(Float, nullable=True)  # Discounted/current price (None если нет скидки)
    first_price = Column(Float, nullable=True)  # Original price (None если не указана)
