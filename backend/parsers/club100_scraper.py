import requests
from bs4 import BeautifulSoup
import logging
from utils.db_utils import parse_price
import time
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

PAGES = [
    "https://www.club100.kz/katalog/obuv/?p=2&p=0",
    "https://www.club100.kz/katalog/obuv/?p=1",
    "https://www.club100.kz/katalog/obuv/?p=1&p=2",
    "https://www.club100.kz/katalog/obuv/?p=2&p=3",
    "https://www.club100.kz/katalog/obuv/?p=3&p=4",
    "https://www.club100.kz/katalog/obuv/?p=4&p=5",
]

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

        category = ["Обувь"]

        return {
            "shop": "Club100",
            "name": name,
            "link": link,
            "first_price": first_price,
            "sale_price": sale_price,
            "category": category,
        }
    except Exception as e:
        logging.warning(f"Ошибка парсинга карточки: {e}")
        return None

def parse_product_details(product_url):
    """Парсит brand и images со страницы товара"""
    html = fetch_html(product_url)
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")

    brand = None
    brand_divs = soup.select('div.parameter.r[itemprop="brand"]')
    if brand_divs:
        first_brand_div = brand_divs[0]
        values_spans = first_brand_div.select('span.values')
        if len(values_spans) >= 2:
            brand = values_spans[1].get_text(strip=True)
        elif len(values_spans) >= 1:
            brand = values_spans[0].get_text(strip=True)

    images = []
    photo_list = soup.select_one('div.photoList')
    if photo_list:
        link_tags = photo_list.find_all('link', itemprop='image')
        for link_tag in link_tags:
            img_href = link_tag.get('href', '')
            if img_href:
                if not img_href.startswith("http"):
                    img_href = "https://www.club100.kz" + img_href
                img_href = img_href.split('?')[0]
                if img_href not in images:
                    images.append(img_href)

    categories = ["Обувь"]
    breadcrumb_tags = soup.select(".breadcrumb a, .breadcrumbs a, nav[aria-label='breadcrumb'] a")
    for crumb in breadcrumb_tags:
        crumb_text = crumb.get_text(strip=True)
        if crumb_text and crumb_text.lower() not in ["главная", "home", "каталог", "catalog", "club100"]:
            categories.append(crumb_text)

    return {
        "brand": brand,
        "images": images if images else None,
        "category": list(set(categories))
    }

def parse_club100():
    parsed_products = []
    seen_links = set()
    
    for page_num, url in enumerate(PAGES, 1):
        html = fetch_html(url)
        if not html:
            logging.warning(f"Не удалось получить HTML для страницы {page_num}, пропускаем")
            continue

        soup = BeautifulSoup(html, "html.parser")
        
        products_list = soup.select_one('.productsList, .list')
        if not products_list:
            logging.warning(f"Не найден контейнер товаров на странице {page_num}")
            continue
        
        cards = products_list.select('.cover')
        
        if not cards:
            logging.info(f"Не найдены товары на странице {page_num}, пропускаем")
            continue

        logging.info(f"Страница {page_num}: найдено {len(cards)} карточек")

        for card in cards:
            product = parse_product_card(card)
            if product and product.get("link"):
                if product["link"] in seen_links:
                    continue
                seen_links.add(product["link"])
                
                details = parse_product_details(product["link"])
                if details.get("brand"):
                    product["brand"] = details["brand"]
                if details.get("images"):
                    product["images"] = details["images"]
                if details.get("category"):
                    product["category"] = details["category"]
                
                parsed_products.append(product)
            time.sleep(1)

    logging.info(f"✅ Club100: всего собрано {len(parsed_products)} товаров")
    return parsed_products
