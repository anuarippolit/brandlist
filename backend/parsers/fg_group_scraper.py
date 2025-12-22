import requests
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

FG_CATEGORIES = [320]
MAX_PAGES = 1000
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

    try:
        sale_price_raw = float(product.get("salePrice", 0))
    except (TypeError, ValueError):
        sale_price_raw = 0

    try:
        first_price_raw = float(product.get("firstPrice", 0))
    except (TypeError, ValueError):
        first_price_raw = 0

    if sale_price_raw and first_price_raw and sale_price_raw < first_price_raw:
        first_price = first_price_raw
        sale_price = sale_price_raw
    else:
        first_price = first_price_raw if first_price_raw else sale_price_raw
        sale_price = None

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
    category_from_path = category_data.split(" / ") if category_data else []
    
    category_from_path_clean = [c.strip() for c in category_from_path if c.strip() and c.strip().lower() != "обувь"]
    
    category = []
    if manual_cat:
        category.append(manual_cat)
    for cat in category_from_path_clean:
        if cat not in category:
            category.append(cat)

    return {
        "shop": "FG group",
        "name": name,
        "brand": brand,
        "category": category,
        "images": images if images else [],
        "link": link,
        "first_price": first_price,
        "sale_price": sale_price,
    }

def parse_fg_group():
    parsed_products = []

    for cat_id in FG_CATEGORIES:
        page_number = 1
        seen_links = set()
        total_pages = None
        
        while True:
            if page_number > MAX_PAGES:
                logging.warning(f"Достигнут лимит {MAX_PAGES} страниц для категории {cat_id}, останавливаемся")
                break
                
            logging.info(f"📦 Категория {cat_id} — парсим страницу {page_number}")

            url = (
                f"{BASE_URL}?expand=pagination,products,products.specifications,"
                f"products.skusList,products.otherColors,products.otherColors.catalogImages,"
                f"products.catalogImages&attributeValueIds[]={cat_id}&page={page_number}"
            )

            data = fetch_json(url)
            if not data:
                logging.warning(f"⚠️ Нет данных для категории {cat_id} на странице {page_number}, останавливаемся")
                break

            if total_pages is None and "pagination" in data:
                pagination = data.get("pagination", {})
                if isinstance(pagination, dict):
                    total_pages = (
                        pagination.get("totalPages") or
                        pagination.get("total_pages") or
                        pagination.get("pages") or
                        pagination.get("lastPage") or
                        None
                    )
                    if total_pages:
                        logging.info(f"📊 Категория {cat_id}: всего страниц {total_pages}")

            products = data.get("products", [])
            if not products:
                logging.info(f"✅ Категория {cat_id} — страница {page_number} пуста, парсинг завершен")
                break

            logging.info(f"Страница {page_number}: найдено {len(products)} товаров")

            for product in products:
                parsed = parse_product(product, cat_id)
                if parsed:
                    if parsed["link"] in seen_links:
                        continue
                    seen_links.add(parsed["link"])
                    parsed_products.append(parsed)
            
            if total_pages and page_number >= total_pages:
                logging.info(f"Достигнута последняя страница ({total_pages}) для категории {cat_id}")
                break
            
            page_number += 1

    logging.info(f"✅ FG Group: всего собрано {len(parsed_products)} товаров")
    return parsed_products

if __name__ == "__main__":
    all_products = parse_fg_group()

    print(f"🧪 Всего товаров: {len(all_products)}")
    for product in all_products:
        print("\n" + "-" * 60)
        for key, val in product.items():
            print(f"{key}: {val}")
