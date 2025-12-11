# from openai import AsyncOpenAI
# import json
# from system.config import settings

# # Инициализация клиента OpenAI
# client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# # Значения по умолчанию для всех фильтров
# DEFAULT_FILTERS = {
#   "category": ["ANY"],
#   "brand": ["ANY"],
#   "model": "ANY",
#   "size": "ANY",
#   "price_max": "ANY",
#   "gender": ["ANY"],
#   "color": ["ANY"],
#   "excluded_category": [],
#   "excluded_brand": [],
#   "excluded_model": [],
#   "excluded_color": []
# }

# # Основная функция: извлечение фильтров из текста
# async def extract_filters_from_text(user_text: str) -> dict:
#     system_prompt = generate_system_prompt()

#     try:
#         response = await client.chat.completions.create(
#             model="gpt-4.1-nano",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_text}
#             ],
#             temperature=0.0,
#         )

#         print("🧠 Used model:", response.model)
#         print("🧠 OpenAI response received")
#         content = response.choices[0].message.content

#         filters = json.loads(content)
#         for key, val in DEFAULT_FILTERS.items():
#             filters.setdefault(key, val)

#         # Fix sizes if needed
#         size_raw = filters.get("size")
#         if isinstance(size_raw, str) and "," in size_raw:
#             filters["size"] = [s.strip() for s in size_raw.split(",")]
#         elif isinstance(size_raw, str):
#             filters["size"] = [size_raw.strip()]

#         return filters

#     except json.JSONDecodeError as json_err:
#         print(f"❌ JSON parsing error: {json_err}")
#         print(f"Content received: {content}")
#         return DEFAULT_FILTERS.copy()

#     except Exception as e:
#         print(f"❌ Error in extract_filters_from_text: {str(e)}")
#         import traceback; traceback.print_exc()
#         return DEFAULT_FILTERS.copy()

# # Новый компактный prompt
# SYSTEM_PROMPT = """
# Ты — AI-ассистент по поиску одежды и обуви. Твоя задача: проанализировать сообщение пользователя и извлечь фильтры поиска.

# Извлеки и заполни следующие поля:
# - category: список категорий из filters.json (ищи самые похожие, если точного совпадения нет)
# - brand: список брендов из filters.json (если есть бренд из семейства — включи всю семью)
# - model: строка, если встречается конкретное название модели
# - size: строка (напр. "42" или "M")
# - price_max: максимальная цена, если указана
# - gender: ["man"], ["woman"], ["boy"], ["girl"], ["newborn"] или ["ANY"]
# - color: список цветов из filters.json (если есть цвет из семейства - включи всю семью)
# - excluded_category, excluded_brand, excluded_model: списки, если пользователь явно исключает что-то

# Если фильтр не указан — заполни как "ANY" (или пустой список для excluded_параметров).

# ВАЖНО:
# - Используй только значения из filters.json.
# - При отсутствии точного совпадения в category, ищи ближайшие по смыслу. Примеры:
#   - "штаны" или "трико" → "брюки"
#   - "свитшот", "худи", "толстовка", "кофта" → все категории из этой группы
#   - "сланцы", "вьетнамки", "шлепанцы" → совместимы
#   - "туфли" и "лоферы" — родственные
# - Запрос включающий в себя слово Samba - "Samba" это модель!!! 
# - Если пользователь говорит "не [что-то]" — ты обязан:
#   1. Найти в filters.json все категории, максимально близкие к этому слову — и добавить их в `excluded_category`
#   2. Само слово "[что-то]" — в том виде, как оно написано пользователем — обязательно добавить в `excluded_model`
#   ❗ Никогда не добавляй такие слова в `model`, даже если они выглядят как название

#   Например:
#   - "не спортивные" → excluded_category = ["Спортивная одежда", "Кроссовки", "Кеды"], IMPORTANT - excluded_model = ["спортивные", "тайтсы", легинсы"], model = "ANY"

# ОСОБЫЕ ПРАВИЛА ПО КАТЕГОРИЯМ:

# - Если пользователь ищет **кроссовки**, обязательно добавь также категории:
#   → "Спортивная обувь", "Кроссовки", "Кеды"

# - Но если пользователь ищет **кеды**, добавляй ТОЛЬКО категорию "Кеды" — **не** добавляй "Кроссовки" или "Спортивная обувь"

# Бренды:
# - Если бренд входит в семейство (brand_families из filters.json) — добавь все бренды из семьи.
# - **Если слово не найдено в списке брендов (и его нет ни в одной brand_families) — НЕ добавляй его в brand.**
# - **Вместо этого, если оно похоже на конкретное название, присвой его в model.**
# - Если бренд не найден — brand = ["ANY"]

# Пол:
# - Примеры: "для девочки" → ["girl"], "для мужчин" → ["man"], "детское"  → ["boy", "girl", "newborn"], "взрослые"  → ["man", "woman"]
# - Если не указан — ["ANY"]

# Верни ответ строго в формате JSON:
# {
#   "category": ["ANY"],
#   "brand": ["ANY"],
#   "model": "ANY",
#   "size": "ANY",
#   "price_max": "ANY",
#   "gender": ["ANY"],
#   "color": ["ANY"],
#   "excluded_category": [],
#   "excluded_brand": [],
#   "excluded_model": [],
#   "excluded_color": []
# }

# Никаких комментариев или пояснений — только JSON-объект.
# """

# def generate_system_prompt():
#     return SYSTEM_PROMPT
