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
    colors = Column(ARRAY(String), nullable=True)
    images = Column(ARRAY(String), nullable=True)
    sizes = Column(ARRAY(String), nullable=True)
    category = Column(ARRAY(String), nullable=True)
    gender = Column(ARRAY(String), nullable=True)

    # Прочее
    link = Column(String, nullable=True, unique=True)
    brand = Column(String, nullable=True)
    sale_price = Column(Float, nullable=True)
    first_price = Column(Float, nullable=True)

    fam_category = Column(String, nullable=True, index=True)
