import requests
import logging
from bs4 import BeautifulSoup
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

FG_CATEGORIES = [320, 322, 140, 156, 410]
PAGE_LIMIT = 1
BASE_URL = "https://api.frgroup.kz/v3/catalog"

def fetch_json(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка запроса: {e}")
        return None

def fetch_images_from_product_page(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        image_tags = soup.select("div.product_image.swiper-slide img.product-img")
        images = []
        for tag in image_tags:
            img_url = tag.get("data-src") or tag.get("src")
            if img_url and img_url not in images:
                images.append(img_url)

        if not images:
            logging.warning(f"[{url}] Не удалось найти изображения по селектору.")
        return images

    except Exception as e:
        logging.warning(f"❌ Ошибка парсинга изображений с {url}: {e}")
        return []

def parse_product(product, cat_id):
    specifications = product.get("specifications", {})

    name = product.get("title", "").strip()
    brand = specifications.get("brand", {}).get("title", "").strip()
    link = product.get("url", "").strip()

    images = fetch_images_from_product_page(link)

    color = specifications.get("color", {}).get("title", "").strip()
    sizes = [sku.get("sizeValue", "") for sku in product.get("skusList", []) if sku.get("isAvailable")]

    sale_price = product.get("salePrice", 0)
    first_price = product.get("firstPrice", 0)

    gender_map = {
        "Мужчинам": ["man"],
        "Женщинам": ["woman"],
        "Мальчикам": ["kid", "boy"],
        "Девочкам": ["kid", "girl"],
    }
    gender_raw = specifications.get("gender", {}).get("title", "").strip()
    gender = gender_map.get(gender_raw, [])

    manual_category_map = {
        320: "Обувь",
        322: "Одежда",
        140: "Аксессуары",
        156: "Белье",
        410: "Спорт",
    }
    manual_cat = manual_category_map.get(cat_id)
    category_data = specifications.get("category", {}).get("path", "")
    category_from_path = list(set(category_data.split(" / "))) if category_data else []
    category = [manual_cat] + category_from_path if manual_cat else category_from_path

    return {
        "shop": "FG group",
        "name": name,
        "brand": brand,
        "category": category,
        "gender": gender,
        "colors": [color] if color else [],
        "images": images,
        "link": link,
        "sizes": sizes,
        "price_original": first_price,
        "price_discounted": sale_price,
    }

def parse_fg_group(limit_per_category=2):
    parsed_products = []

    for cat_id in FG_CATEGORIES:
        found = 0
        page_number = 1

        while True:
            logging.info(f"📦 Категория {cat_id} — парсим страницу {page_number}")

            url = (
                f"{BASE_URL}?expand=pagination,products,products.specifications,"
                f"products.skusList,products.otherColors,products.otherColors.catalogImages,"
                f"products.catalogImages&attributeValueIds[]={cat_id}&page={page_number}"
            )

            data = fetch_json(url)
            if not data:
                logging.warning(f"⚠️ Нет данных для категории {cat_id} на странице {page_number}")
                break

            products = data.get("products", [])
            if not products:
                logging.info(f"✅ Категория {cat_id} — страница {page_number} пуста, остановка.")
                break

            for product in products:
                parsed_products.append(parse_product(product, cat_id))
                found += 1
                if found >= limit_per_category:
                    logging.info(f"🎯 Достигли лимита {limit_per_category} для категории {cat_id}")
                    break

            if found >= limit_per_category:
                break

            page_number += 1

    return parsed_products


if __name__ == "__main__":
    all_products = parse_fg_group(limit_per_category=2)

    print("🧪 По два товара на каждую категорию:")
    for product in all_products:
        print("\n" + "-" * 60)
        for key, val in product.items():
            print(f"{key}: {val}")
