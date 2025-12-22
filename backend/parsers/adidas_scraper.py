import requests
import logging
from utils.db_utils import parse_price
import time
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

API_BASE_URL = "https://catalog.adidas.kz/v1/catalog/obuv"
MAX_PAGES = 1000
PRODUCTS_PER_PAGE = 48

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Accept": "application/json"
}

def fetch_api_data(page):
    """Получение данных из API."""
    try:
        url = f"{API_BASE_URL}?page={page}&expand=links,counts,attributes,products,products.imagesMainList,products.baseInfo,products.colors.imagesMainList,products.colors.baseInfo,products.sizes&size={PRODUCTS_PER_PAGE}"
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed for page {page}: {e}")
        time.sleep(2)
        return None

def build_image_url(image_id, size="w_1200"):
    """Строит URL изображения из image_id."""
    if not image_id:
        return None
    return f"https://assetmanagerpim-res.cloudinary.com/images/{size}/q_90/{image_id}.WebP"

def parse_product_from_api(product_data):
    """Парсит товар из JSON API."""
    try:
        name = product_data.get("displayName", "").strip()
        if not name:
            return None

        brand = "Adidas"

        url_data = product_data.get("url", {})
        link = url_data.get("absolute") or url_data.get("parent", "")
        if link and not link.startswith("http"):
            link = "https://adidas.kz" + link

        price_data = product_data.get("price", {})
        first_price = price_data.get("first")
        sale_price = price_data.get("sale")
        
        if first_price:
            first_price = float(first_price)
        if sale_price:
            sale_price = float(sale_price)
            if sale_price >= first_price:
                sale_price = None
        else:
            sale_price = None

        images = []
        images_main_list = product_data.get("imagesMainList", {})
        
        main_image = images_main_list.get("main", {})
        if main_image and main_image.get("id"):
            main_img_url = build_image_url(main_image["id"])
            if main_img_url:
                images.append(main_img_url)
        
        hover_image = images_main_list.get("hover", {})
        if hover_image and hover_image.get("id"):
            hover_img_url = build_image_url(hover_image["id"])
            if hover_img_url and hover_img_url not in images:
                images.append(hover_img_url)
        
        plp_image = images_main_list.get("plp", {})
        if plp_image and plp_image.get("id"):
            plp_img_url = build_image_url(plp_image["id"])
            if plp_img_url and plp_img_url not in images:
                images.append(plp_img_url)

        categories = product_data.get("productPath", [])
        if not categories:
            categories = ["Обувь"]
        else:
            if "Обувь" not in categories:
                categories = ["Обувь"] + categories

        return {
            "shop": "Adidas",
            "name": name,
            "brand": brand,
            "link": link,
            "images": images if images else None,
            "first_price": first_price,
            "sale_price": sale_price,
            "category": categories,
        }
    except Exception as e:
        logging.warning(f"Ошибка парсинга товара из API: {e}")
        return None

def parse_adidas():
    parsed_products = []
    page = 1
    seen_links = set()
    total_pages = None
    total_products = None

    while True:
        if page > MAX_PAGES:
            logging.warning(f"Достигнут лимит {MAX_PAGES} страниц, останавливаемся")
            break
            
        logging.info(f"Парсинг страницы {page}...")
        
        api_data = fetch_api_data(page)
        if not api_data:
            logging.warning(f"Не удалось получить данные для страницы {page}, останавливаемся")
            break

        if total_pages is None:
            if "count" in api_data:
                total_products = api_data.get("count", 0)
                total_pages = (total_products + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE
                logging.info(f"📊 Всего товаров в каталоге: {total_products}, страниц: {total_pages}")
            elif "counts" in api_data:
                counts = api_data.get("counts", {})
                if isinstance(counts, dict) and "products" in counts:
                    total_products = counts.get("products", 0)
                    total_pages = (total_products + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE
                    logging.info(f"📊 Всего товаров в каталоге: {total_products}, страниц: {total_pages}")

        products = api_data.get("products", [])
        if not products:
            logging.info(f"Не найдены товары на странице {page}, парсинг завершен")
            break

        logging.info(f"Страница {page}: найдено {len(products)} товаров")

        for product_data in products:
            product = parse_product_from_api(product_data)
            if product:
                if product["link"] in seen_links:
                    continue
                seen_links.add(product["link"])
                parsed_products.append(product)
        
        if total_pages and page >= total_pages:
            logging.info(f"Достигнута последняя страница ({total_pages}) из API count")
            break
            
        if len(products) < PRODUCTS_PER_PAGE:
            logging.info(f"Получено меньше товаров ({len(products)}) чем размер страницы ({PRODUCTS_PER_PAGE}), это последняя страница")
            break
        
        page += 1
        time.sleep(1)

    logging.info(f"✅ Adidas: всего собрано {len(parsed_products)} товаров с {page-1} страниц")
    return parsed_products

if __name__ == "__main__":
    all_products = parse_adidas()
    print(f"🧪 Всего товаров: {len(all_products)}")
    for product in all_products[:3]:
        print("\n" + "-" * 60)
        for key, val in product.items():
            print(f"{key}: {val}")
