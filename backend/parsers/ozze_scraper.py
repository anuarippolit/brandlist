import requests
from bs4 import BeautifulSoup
import logging
from utils.db_utils import parse_price  # ✅ Correct import for price parsing
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

CATEGORIES = ["katalog-1-332e60", "odezhda", "obuv-3", "obuv", "katalog-1-203ea8", "katalog-1-95871b"]
PAGE_LIMIT = 2

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

KNOWN_BRANDS = ["LACOSTE", "NORTH SAILS", "CONVERSE"]

def fetch_html(url):
    """Получение HTML страницы."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        time.sleep(5)
        return None

def translate_lacoste_size(raw_size):
    """Трансформация размеров Lacoste в стандартные."""
    size_map = {
        "T2": "XS", "T3": "S", "T4": "M", "T5": "M/L", "T6": "L", "T7": "XL", "T8": "XXL", "T9": "3XL",
        "T00": "XXS", "TS": "S", "TM": "M", "TL": "L", "TXL": "XL", "TXXL": "XXL", "T110": "110 cm"
    }
    return size_map.get(raw_size.strip().upper(), raw_size)

def parse_product_card(card):
    """Парсинг карточки товара."""
    try:
        # Name and Link
        name_tag = card.select_one("a.is-card-title-link")
        name = name_tag.text.strip() if name_tag else "No Name"
        link = "https://www.ozze.kz" + name_tag["href"] if name_tag else "No Link"

        # Brand (based on known brands)
        brand = next((b for b in KNOWN_BRANDS if b in name.upper()), "Unknown Brand")

        # Image
        img_tag = card.select_one("img.is-card-link-pic-img")
        image_url = img_tag.get("data-src", "No Image") if img_tag else "No Image"

        # Sizes
        sizes = []
        options = card.select("select[name='variant_id'] option")
        for opt in options:
            if "/" in opt.text:
                raw = opt.text.split("/")[-1].strip()
                translated = translate_lacoste_size(raw)
                sizes.append(translated)

        # Prices
        price_tag = card.select_one("span.is-card-prices-cur-active") or card.select_one("span.is-card-prices-cur")
        sale_price = parse_price(price_tag.get_text(strip=True)) if price_tag else None

        first_tag = card.select_one("span.is-card-prices-old")
        first_price = parse_price(first_tag.get_text(strip=True)) if first_tag else None

        # Category (guessing from name if possible)
        parts = name.split()
        category = " ".join(parts[:-1]) if len(parts) > 1 else "Unknown Category"

        return {
            "shop": "ozze",
            "name": name,
            "image_url": image_url,
            "link": link,
            "sizes": sizes,
            "brand": brand,
            "sale_price": sale_price,
            "first_price": first_price,
            "category": [category] if isinstance(category, str) else ["Unknown Category"]
        }
    except Exception as e:
        logging.warning(f"Ошибка парсинга карточки: {e}")
        return None

def parse_ozze():
    """Парсит сайт Ozze и возвращает список продуктов."""
    all_products = []

    for category in CATEGORIES:
        for page in range(1, PAGE_LIMIT + 1):
            url = f"https://www.ozze.kz/collection/{category}?PAGEN_1={page}"
            html = fetch_html(url)
            if not html:
                continue

            soup = BeautifulSoup(html, "lxml")
            cards = soup.select("div.is-card")
            logging.info(f"[{category}] Страница {page}: найдено {len(cards)} карточек")

            for card in cards:
                product = parse_product_card(card)
                if product:
                    all_products.append(product)
                time.sleep(2)  # Небольшая задержка чтобы не нагружать сайт

    return all_products
