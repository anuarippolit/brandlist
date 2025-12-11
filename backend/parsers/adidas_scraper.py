import requests
import logging
from utils.db_utils import parse_price

  # Функция для сохранения данных

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "https://catalog.adidas.kz/v1/catalog/"
ADIDAS_CATEGORIES = ["obuv", "odezhda", "aksessuary"]
PAGE_LIMIT = 2  # Количество страниц для парсинга


def fetch_json(url):
    """Функция делает GET-запрос и возвращает JSON."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Выбросит исключение при плохом статус-коде
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка запроса: {e}")
        return None


def parse_product(product, shop_name="Adidas"):
    """Функция извлекает информацию о продукте."""
    parsed_products = []

    colors = product.get("colors", [])
    for color in colors:
        price_info = color.get("price", {})

        image_id = color.get("imagesMainList", {}).get("main", {}).get("id")
        image_url = f"https://assetmanagerpim-res.cloudinary.com/images/w_800/q_90/{image_id}.WebP" if image_id else "No Image"

        product_info = {
            "shop": shop_name,
            "name": product.get("displayName", "No Name"),
            "color": color.get("color", "Unknown Color"),
            "image_url": image_url,
            "link": color.get("url", {}).get("absolute", "No Link"),
            "sizes": [size["title"] for size in product.get("sizes", []) if size.get("isAvailable", False)],
            "brand": shop_name + product.get("division", "Unknown Brand"),
            "sale_price": parse_price(price_info.get("sale")),
            "first_price": parse_price(price_info.get("first")),
            "category": [color.get("productPath", "Unknown Category")],
        }

        parsed_products.append(product_info)

    return parsed_products


def parse_adidas():
    """Функция парсит сайт Adidas и возвращает список товаров."""
    parsed_products = []

    for category in ADIDAS_CATEGORIES:
        for page_number in range(1, PAGE_LIMIT + 1):
            url = f"{BASE_URL}{category}?page={page_number}&expand=links,counts,attributes,products,products.imagesMainList,products.baseInfo,products.colors.imagesMainList,products.colors.baseInfo,products.sizes&size=48"

            data = fetch_json(url)
            if not data:
                logging.warning(f"Не удалось получить данные для {category}, страница {page_number}")
                continue

            products = data.get("products", [])
            for product in products:
                parsed_products.extend(parse_product(product))  # Добавляем все цвета продукта

    return parsed_products

