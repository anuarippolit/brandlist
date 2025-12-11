# from sqlalchemy import create_engine, select
# from sqlalchemy.orm import sessionmaker
# from system.config import settings
# from system.db.models import Product
#
# # Correct setup for database
# engine = create_engine(settings.database_url)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# async def fetch_products(categories: list):
#     session = SessionLocal()
#     try:
#         lowercase_categories = [cat.lower() for cat in categories]
#
#         stmt = select(Product)
#         results = session.execute(stmt).scalars().all()
#
#         filtered = []
#         for product in results:
#             if not product.category:
#                 continue
#             product_categories = [c.lower() for c in product.category]
#             if any(cat in product_categories for cat in lowercase_categories):
#                 filtered.append(product)
#
#         return filtered
#
#     except Exception as e:
#         print(f"❌ Error fetching products: {e}")
#         return []
#
#     finally:
#         session.close()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from system.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()