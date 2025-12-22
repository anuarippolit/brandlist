import requests
from bs4 import BeautifulSoup
import logging
from utils.db_utils import parse_price
import time
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "https://www.club100.kz/katalog/obuv/"
ALTERNATIVE_CATEGORIES = [
    "https://www.club100.kz/katalog/obuv/category%3Akrossovki/",
    "https://www.club100.kz/katalog/obuv/category%3Abotinki/",
    "https://www.club100.kz/katalog/obuv/brand%3Anike/",
]
MAX_PAGES = 1000

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def fetch_html(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        time.sleep(2)
        return None

def parse_product_card(card):
    try:
        link_tag = card.find('a', href=lambda x: x and '/katalog/' in str(x) and len(str(x).split('/')) >= 4)
        if not link_tag:
            return None
        
        link = link_tag.get("href", "")
        if link and not link.startswith("http"):
            link = "https://www.club100.kz" + link

        img = card.find('img')
        name = None
        if img:
            title = img.get('title', '') or img.get('alt', '')
            if 'для товара' in title:
                name = title.split('для товара')[1].strip()
            elif title:
                name = title.replace('Фотография', '').replace('из', '').strip()
                name = re.sub(r'^\d+\s+\d+\s+', '', name).strip()
        
        if not name:
            return None
        name_lower = name.lower()
        if "nike" in name_lower:
            brand = "Nike"
        elif "jordan" in name_lower:
            brand = "Jordan"
        elif "adidas" in name_lower:
            brand = "Adidas"
        elif "puma" in name_lower:
            brand = "Puma"
        else:
            brand = name.split()[0] if name else "Unknown Brand"

        price_text = ""
        next_element = card.find_next_sibling(['div', 'section', 'span'])
        if next_element:
            price_text = next_element.get_text(strip=True)
        prices = re.findall(r'[\d\s]+₸', price_text)
        if len(prices) >= 2:
            sale_price = parse_price(prices[0])
            first_price = parse_price(prices[1])
        elif len(prices) == 1:
            sale_price = parse_price(prices[0])
            first_price = sale_price
        else:
            sale_price = None
            first_price = None

        images = []
        covers = card.select_one('.covers')
        if covers:
            img_tags = covers.find_all('img')
            for img_tag in img_tags:
                img_src = img_tag.get('data-image') or img_tag.get('src')
                if img_src:
                    if not img_src.startswith("http"):
                        img_src = "https://www.club100.kz" + img_src
                    img_src = img_src.split('?')[0]
                    if img_src not in images:
                        images.append(img_src)

        category = ["Обувь"]

        return {
            "shop": "Club100",
            "name": name,
            "brand": brand,
            "link": link,
            "images": images,
            "first_price": first_price,
            "sale_price": sale_price or first_price,
            "category": category,
        }
    except Exception as e:
        logging.warning(f"Ошибка парсинга карточки: {e}")
        return None

def parse_product_details(product_url):
    html = fetch_html(product_url)
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")

    images = []
    image_selectors = [
        ".product-images img",
        ".product-gallery img",
        ".product-photos img",
        ".gallery img",
        "img.product-image",
        ".swiper-slide img"
    ]
    for selector in image_selectors:
        img_tags = soup.select(selector)
        for img in img_tags:
            img_src = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or img.get("data-zoom-image")
            if img_src and img_src not in images:
                if not img_src.startswith("http"):
                    img_src = "https://www.club100.kz" + img_src
                images.append(img_src)
        if images:
            break

    categories = ["Обувь"]
    breadcrumb_tags = soup.select(".breadcrumb a, .breadcrumbs a, nav[aria-label='breadcrumb'] a")
    for crumb in breadcrumb_tags:
        crumb_text = crumb.get_text(strip=True)
        if crumb_text and crumb_text.lower() not in ["главная", "home", "каталог", "catalog", "club100"]:
            categories.append(crumb_text)

    return {
        "images": images if images else None,
        "category": list(set(categories))
    }

def parse_club100():
    parsed_products = []

    urls_to_try = [BASE_URL] + ALTERNATIVE_CATEGORIES
    
    for base_url in urls_to_try:
        page = 1
        seen_links = set()
        
        while True:
            if page > MAX_PAGES:
                logging.warning(f"Достигнут лимит {MAX_PAGES} страниц для {base_url}, останавливаемся")
                break
                
            if page == 1:
                url = f"{base_url}?p=1&p=0"
            elif page == 2:
                url = f"{base_url}?p=1"
            else:
                url = f"{base_url}?p={page-2}&p={page-1}"
            
            html = fetch_html(url)
            if not html:
                logging.warning(f"Не удалось получить HTML для страницы {page}, останавливаемся")
                break

            soup = BeautifulSoup(html, "html.parser")
            
            products_list = soup.select_one('.productsList, .list')
            if not products_list:
                logging.warning(f"Не найден контейнер товаров на странице {page}")
                break
            
            cards = products_list.select('.cover')
            
            if not cards:
                logging.info(f"Не найдены товары на странице {page} для {base_url}, парсинг завершен")
                break

            logging.info(f"Страница {page}: найдено {len(cards)} карточек")

            for card in cards:
                product = parse_product_card(card)
                if product and product.get("link"):
                    if product["link"] in seen_links:
                        continue
                    seen_links.add(product["link"])
                    details = parse_product_details(product["link"])
                    if details.get("images"):
                        product["images"] = details["images"]
                    if details.get("category"):
                        product["category"] = details["category"]
                    parsed_products.append(product)
                time.sleep(1)
            
            page += 1

    logging.info(f"✅ Club100: всего собрано {len(parsed_products)} товаров")
    return parsed_products

if __name__ == "__main__":
    all_products = parse_club100()
    print(f"🧪 Всего товаров: {len(all_products)}")
    for product in all_products[:3]:
        print("\n" + "-" * 60)
        for key, val in product.items():
            print(f"{key}: {val}")
