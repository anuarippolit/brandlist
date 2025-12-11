from sqlalchemy import select, and_, not_, or_, func, cast, Text, exists, literal
from sqlalchemy.dialects.postgresql import array, ARRAY
from system.db.db_service import SessionLocal
from system.db.models import Product
from sqlalchemy.sql import literal_column


import os
import json

FILTERS_PATH = os.path.join(os.path.dirname(__file__), "../data/filters.json")
with open(FILTERS_PATH, "r", encoding="utf-8") as f:
    filters_data = json.load(f)

conversion_map = filters_data.get("size_conversion", {})

# def convert_sizes(sizes, gender):
#     if not isinstance(sizes, list):
#         sizes = [sizes]
#     gender = gender if isinstance(gender, list) else [gender]
#
#     result = set(sizes)
#
#     # Determine which maps to use
#     gender_keys = []
#     if "man" in gender:
#         gender_keys.append("man")
#     if "woman" in gender:
#         gender_keys.append("woman")
#     if "ANY" in gender or not gender_keys:
#         # Fallback: use both maps if gender is ANY or unrecognized
#         gender_keys = ["man", "woman"]
#
#     # Expand sizes
#     for g in gender_keys:
#         gender_map = conversion_map.get(g, {})
#         for s in sizes:
#             ru_equiv = gender_map.get(s.upper())
#             if ru_equiv:
#                 result.update(ru_equiv)
#
#     return list(result)

def convert_sizes(sizes, gender):
    if not isinstance(sizes, list):
        sizes = [sizes]
    gender = gender if isinstance(gender, list) else [gender]

    result = set()

    # Determine which maps to use
    gender_keys = []
    if "man" in gender:
        gender_keys.append("man")
    if "woman" in gender:
        gender_keys.append("woman")
    if "ANY" in gender or not gender_keys:
        gender_keys = ["man", "woman"]

    # Expand sizes across all known mappings (INT → RU + EU)
    for g in gender_keys:
        gender_map = conversion_map.get(g, {})
        for s in sizes:
            norm = s.upper().strip()
            result.add(norm)
            value = gender_map.get(norm)
            if isinstance(value, dict):
                result.update(value.get("ru", []))
                result.update(value.get("eu", []))
            elif isinstance(value, list):  # backward compatibility
                result.update(value)

    return list(result)




def get_products_by_filters(filters: dict, offset: int = 0, limit: int = 20, original_text: str = "", sort: str = "relevance"):
    print("📡 get_products_by_filters — this version is running")
    session = SessionLocal()

    try:
        stmt = select(Product)
        conditions = []

        def valid(v):
            return v and v != "ANY" and v != ["ANY"]

        # Категория (ARRAY text[])
        if valid(filters.get("category")):
            categories = filters["category"]
            exists_conditions = []

            for cat in categories:
                subquery = select(literal(1)).where(
                    or_(
                        func.similarity(func.lower(literal_column("c")), cat.lower()) > 0.6,
                        func.lower(literal_column("c")).like(f"%{cat.lower()}%")
                    )
                ).select_from(func.unnest(Product.category).alias("c"))

                exists_conditions.append(exists(subquery))

            if exists_conditions:
                # ⬅️ объединяем через OR, не AND
                conditions.append(or_(*exists_conditions))

        # Исключённые категории
        for exc in filters.get("excluded_category", []):
            conditions.append(not_(Product.category.op("@>")(cast(array([exc]), ARRAY(Text)))))

        # Бренд (text)
        if valid(filters.get("brand")):
            brands = filters["brand"] if isinstance(filters["brand"], list) else [filters["brand"]]
            conditions.append(or_(*(Product.brand.ilike(f"%{b}%") for b in brands)))

        # Исключённые бренды
        for exc in filters.get("excluded_brand", []):
            conditions.append(not_(Product.brand.ilike(f"%{exc}%")))

        # Размеры (ARRAY text[])
        # if valid(filters.get("size")):
        #     sizes = filters["size"] if isinstance(filters["size"], list) else [filters["size"]]
        #     conditions.append(Product.sizes.op("&&")(cast(array(sizes), ARRAY(Text))))

        if valid(filters.get("size")):
            sizes = filters["size"] if isinstance(filters["size"], list) else [filters["size"]]
            gender = filters.get("gender", ["ANY"])
            sizes = convert_sizes(sizes, gender)

            # Поддержка размеров в формате "46/48"
            size_conditions = []
            for size in sizes:
                size_conditions.append(
                    func.array_to_string(Product.sizes, ',').ilike(f"%{size}%")
                )

            if size_conditions:
                conditions.append(or_(*size_conditions))

        # Максимальная цена
        if valid(filters.get("price_max")):
            try:
                price = float(filters["price_max"])
                conditions.append(Product.sale_price <= price)
            except ValueError:
                pass

        # Название модели (поиск по имени товара с fuzzy match)
        if valid(filters.get("model")):
            model = filters["model"]
            sim_expr = func.similarity(func.lower(Product.name), model.lower())
            model_match = or_(
                func.lower(Product.name).ilike(f"%{model.lower()}%"),
                sim_expr > 0.25
            )
            conditions.append(model_match)
            stmt = stmt.order_by(sim_expr.desc())

        # Excluded model words (fuzzy match in product name)
        for exc in filters.get("excluded_model", []):
            conditions.append(not_(func.lower(Product.name).ilike(f"%{exc.lower()}%")))

        # Пол (ARRAY text[])
        if valid(filters.get("gender")):
            gender = filters["gender"] if isinstance(filters["gender"], list) else [filters["gender"]]
            conditions.append(Product.gender.op("&&")(cast(array(gender), ARRAY(Text))))

        # Цвета (ARRAY text[])
        if valid(filters.get("color")):
            colors = filters["color"] if isinstance(filters["color"], list) else [filters["color"]]
            conditions.append(Product.colors.op("&&")(cast(array(colors), ARRAY(Text))))

        if conditions:
            print("🔎 SQLAlchemy conditions:")
            for c in conditions:
                print("   →", str(c))
            stmt = stmt.where(and_(*conditions))

        # ✅ Sorting block — place this right after `stmt = stmt.where(...)`
        if sort == "price_asc":
            stmt = stmt.order_by(Product.sale_price.asc().nullslast())
        elif sort == "price_desc":
            stmt = stmt.order_by(Product.sale_price.desc().nullslast())
        elif not valid(filters.get("model")):
            stmt = stmt.order_by(Product.id.desc())  # Fallback relevance if model not present

        # Apply pagination last
        stmt = stmt.offset(offset).limit(limit)

        print("🧾 FINAL SQL:", stmt)
        return session.execute(stmt).scalars().all()

    finally:
        session.close()
