import re
import requests
from bs4 import BeautifulSoup
import logging
from utils.db_utils import parse_price  # ✅ Correct new import

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

CATEGORIES = ["muzhchinam"]
PAGE_LIMIT = 1

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
}

def fetch_html(url, retries=3):
    """Fetches HTML from a URL with retries."""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {url}: {e} (attempt {attempt+1}/{retries})")
            time.sleep(5)
    return None

def parse_product_page(url):
    """Parses a single product page."""
    html = fetch_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "lxml")
    try:
        title_tag = soup.find("h1", class_="entry-title")
        name = title_tag.get_text(strip=True) if title_tag else (
            soup.title.get_text().split("|")[0].strip() if soup.title else "No Name"
        )

        brand = ""
        brand_div = soup.find("div", class_="wd-product-brands")
        if brand_div:
            brand_a = brand_div.find("a")
            if brand_a:
                brand = brand_a.get_text(strip=True)

        link = url

        image_url = ""

        price_block = soup.find("p", class_="price")
        first_price = None
        sale_price = None
        if price_block:
            ins_tag = price_block.find("ins")
            del_tag = price_block.find("del")
            if ins_tag:
                sale_price = parse_price(ins_tag.get_text(strip=True))
            if del_tag:
                first_price = parse_price(del_tag.get_text(strip=True))
            if not ins_tag and price_block.get_text(strip=True):
                first_price = parse_price(price_block.get_text(strip=True))

        sizes = []
        sizes_div = soup.find("div", class_="vi-wpvs-variation-wrap")
        if sizes_div:
            size_elements = sizes_div.find_all("div", class_="vi-wpvs-option-wrap-default")
            for elem in size_elements:
                class_attr = elem.get("class")
                if isinstance(class_attr, list) and "vi-wpvs-hidden" not in class_attr:
                    span = elem.find("span")
                    if span:
                        size_text = span.get_text(strip=True)
                        if size_text and "выберите" not in size_text.lower():
                            sizes.append(size_text)

        categories = []
        breadcrumb = soup.find("nav", class_="woocommerce-breadcrumb")
        if breadcrumb:
            for a in breadcrumb.find_all("a"):
                cat_text = a.get_text(strip=True)
                if cat_text:
                    categories.append(cat_text)

        return {
            "shop": "Copa",
            "name": name,
            "brand": brand,
            "link": link,
            "image_url": image_url,
            "first_price": first_price,
            "sale_price": sale_price,
            "sizes": sizes,
            "category": categories
        }
    except Exception as e:
        logging.warning(f"Ошибка парсинга продукта {url}: {e}")
        return None

def parse_copa():
    """Парсит каталог Copa.kz и возвращает список продуктов."""
    all_products = []
    for category in CATEGORIES:
        for page in range(1, PAGE_LIMIT + 1):
            if page == 1:
                page_url = f"https://copa.kz/shop/?filter_pol={category}&query_type_pol=or"
            else:
                page_url = f"https://copa.kz/shop/page/{page}/?filter_pol={category}&query_type_pol=or"
            logging.info(f"Обработка {page_url}")

            html = fetch_html(page_url)
            if not html:
                continue

            soup = BeautifulSoup(html, "lxml")
            product_cards = soup.find_all("a", class_="product-image-link")
            logging.info(f"[{category}] Страница {page}: найдено {len(product_cards)} товаров")

            for card in product_cards:
                product_link = card.get("href")
                img_card = card.find("img", class_="attachment-large size-large")
                image_url_from_card = img_card["src"] if img_card and img_card.has_attr("src") else "No Image"

                if not product_link:
                    continue

                logging.info(f"Парсинг товара: {product_link}")
                product = parse_product_page(product_link)
                if product:
                    product["image_url"] = image_url_from_card
                    all_products.append(product)

                time.sleep(2)  # небольшая задержка между запросами
    return all_products
