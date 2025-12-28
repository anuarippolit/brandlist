import requests
from bs4 import BeautifulSoup
import logging
import time
import re

def parse_salomon_price(value):
    """
    Parses a price string from Salomon website to float.
    Salomon uses comma as thousands separator (e.g., 92,900 ₸ = 92900.0)
    """
    if isinstance(value, (int, float)):
        return float(value)
    if not value or not isinstance(value, str):
        return None
    
    # Remove all non-digit characters except dots and commas
    cleaned = re.sub(r"[^\d.,]", "", value)
    
    # Salomon prices use comma as thousands separator (e.g., "92,900" = 92900)
    # If there's a comma, it's always a thousands separator, not decimal
    if ',' in cleaned:
        # Remove comma (thousands separator)
        cleaned = cleaned.replace(',', '')
    
    try:
        return float(cleaned)
    except ValueError:
        return None

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URLS = {
    "women": "https://salomon.kz/zhenshchinam/obuv",
    "men": "https://salomon.kz/muzhchinam/obuv",
    "children": "https://salomon.kz/detyam/obuv"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def fetch_html(url):
    """Fetch HTML content from URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for {url}: {e}")
        time.sleep(2)
        return None

def parse_product_card(card):
    """Parse a single product card from the listing page."""
    try:
        name_tag = card.find('a', href=True)
        if not name_tag:
            return None
        
        link = name_tag.get('href', '')
        if not link or link == '#' or 'filter' in link.lower() or 'javascript' in link.lower():
            return None
        
        if link and not link.startswith('http'):
            link = 'https://salomon.kz' + link
        
        name = name_tag.get_text(strip=True)
        if not name:
            # Try alternative selectors
            name_elem = card.find('h2') or card.find('h3') or card.find(class_=re.compile('name|title', re.I))
            if name_elem:
                name = name_elem.get_text(strip=True)
        
        if not name or name.lower() in ['фильтр', 'filter', 'сортировка', 'sort']:
            return None
        
        if '/zhenshchinam/' not in link and '/muzhchinam/' not in link and '/detyam/' not in link:
            return None
        
        # Brand is always Salomon
        brand = "Salomon"
        
        price_text = None
        price_elem = card.find(class_=re.compile('price', re.I))
        if price_elem:
            price_text = price_elem.get_text(strip=True)
        else:
            card_text = card.get_text()
            price_match = re.search(r'([\d\s,]+)\s*₸', card_text)
            if price_match:
                price_text = price_match.group(1).strip()
        
        first_price = parse_salomon_price(price_text) if price_text else None
        sale_price = None  # Salomon might not have sale prices on listing page
        
        category = ["Обувь"]
        
        # Images will be parsed from product detail page
        return {
            "shop": "Salomon",
            "name": name,
            "brand": brand,
            "link": link,
            "images": [],  # Will be filled from product detail page
            "first_price": first_price,
            "sale_price": sale_price,
            "category": category,
        }
    except Exception as e:
        logging.warning(f"Ошибка парсинга карточки: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_product_details(product_url):
    """Parse product details page to extract all images."""
    html = fetch_html(product_url)
    if not html:
        return {}
    
    soup = BeautifulSoup(html, 'html.parser')
    images = []
    
    # Find the image container with id="list_product_image_middle"
    image_container = soup.find('span', id='list_product_image_middle')
    if image_container:
        # Find all <a> tags with class="zoom" - these contain full-size image URLs
        zoom_links = image_container.find_all('a', class_='zoom')
        for link in zoom_links:
            img_href = link.get('href', '')
            if img_href:
                if not img_href.startswith('http'):
                    img_href = 'https://salomon.kz' + img_href
                img_href = img_href.split('?')[0]
                # Clean up URL - sometimes has spaces in filename
                img_href = img_href.replace(' ', '%20')
                # Remove "full_" prefix from filename (e.g., full_475266__2.jpg -> 475266__2.jpg)
                img_href = img_href.replace('/full_', '/').replace('full_', '')
                if img_href not in images:
                    images.append(img_href)
        
        if not images:
            img_tags = image_container.find_all('img')
            for img in img_tags:
                img_src = img.get('src') or img.get('data-src')
                if img_src:
                    if not img_src.startswith('http'):
                        img_src = 'https://salomon.kz' + img_src
                    img_src = img_src.split('?')[0]
                    img_src = img_src.replace(' ', '%20')
                    # Remove "full_" prefix from filename
                    img_src = img_src.replace('/full_', '/').replace('full_', '')
                    if img_src not in images:
                        images.append(img_src)
    
    if not images:
        # Try finding images in product gallery
        gallery_images = soup.select('.product-gallery img, .product-images img, .product-photos img')
        for img in gallery_images:
            img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if img_src and 'img_products' in img_src:
                if not img_src.startswith('http'):
                    img_src = 'https://salomon.kz' + img_src
                img_src = img_src.split('?')[0]
                img_src = img_src.replace(' ', '%20')
                # Remove "full_" prefix from filename
                img_src = img_src.replace('/full_', '/').replace('full_', '')
                if img_src not in images:
                    images.append(img_src)
    
    # Sort images by number in filename (e.g., 475266__1.jpg, 475266__2.jpg, ...)
    def extract_image_number(img_url):
        """Extract number from image filename for sorting (e.g., 475266__2.jpg -> 2)"""
        match = re.search(r'__(\d+)\.', img_url)
        if match:
            return int(match.group(1))
        return 0  # If no number found, put at the beginning
    
    if images:
        images.sort(key=extract_image_number)
    
    categories = ["Обувь"]
    breadcrumb = soup.select('.breadcrumb a, .breadcrumbs a')
    for crumb in breadcrumb:
        crumb_text = crumb.get_text(strip=True)
        if crumb_text and crumb_text.lower() not in ['главная', 'home', 'salomon']:
            if crumb_text not in categories:
                categories.append(crumb_text)
    
    return {
        "images": images if images else None,
        "category": list(set(categories))
    }

def parse_salomon():
    """Main parser function for Salomon website."""
    parsed_products = []
    seen_links = set()
    
    # Women's shoes with pagination (0, 20, 40, 60, 80, 100, 120, 140)
    women_url = BASE_URLS["women"]
    for start in [0, 20, 40, 60, 80, 100, 120, 140]:
        url = f"{women_url}?start={start}" if start > 0 else women_url
        logging.info(f"Парсинг женской обуви: {url}")
        
        html = fetch_html(url)
        if not html:
            logging.warning(f"Не удалось получить HTML для {url}")
            continue
        
        soup = BeautifulSoup(html, 'html.parser')
        
        cards = soup.select('.product-item, .product-card, .product, article.product, .item-product, [class*="product"]')
        
        if not cards:
            # Try alternative selectors
            cards = soup.find_all('div', class_=re.compile('product|item', re.I))
        
        if not cards:
            logging.warning(f"Не найдены карточки товаров на {url}")
            continue
        
        logging.info(f"Найдено {len(cards)} карточек на странице {url}")
        
        for card in cards:
            product = parse_product_card(card)
            if product and product.get('link'):
                if product['link'] in seen_links:
                    continue
                seen_links.add(product['link'])
                
                details = parse_product_details(product['link'])
                if details.get('images'):
                    product['images'] = details['images']
                if details.get('category'):
                    product['category'] = details['category']
                
                parsed_products.append(product)
                time.sleep(0.5)
        
        time.sleep(1)
    
    # Men's shoes with pagination (0, 20, 40, 60, 80, 100, 120, 140)
    men_url = BASE_URLS["men"]
    for start in [0, 20, 40, 60, 80, 100, 120, 140]:
        url = f"{men_url}?start={start}" if start > 0 else men_url
        logging.info(f"Парсинг мужской обуви: {url}")
        
        html = fetch_html(url)
        if not html:
            logging.warning(f"Не удалось получить HTML для {url}")
            continue
        
        soup = BeautifulSoup(html, 'html.parser')
        
        cards = soup.select('.product-item, .product-card, .product, article.product, .item-product, [class*="product"]')
        
        if not cards:
            cards = soup.find_all('div', class_=re.compile('product|item', re.I))
        
        if not cards:
            logging.warning(f"Не найдены карточки товаров на {url}")
            continue
        
        logging.info(f"Найдено {len(cards)} карточек на странице {url}")
        
        for card in cards:
            product = parse_product_card(card)
            if product and product.get('link'):
                if product['link'] in seen_links:
                    continue
                seen_links.add(product['link'])
                
                details = parse_product_details(product['link'])
                if details.get('images'):
                    product['images'] = details['images']
                if details.get('category'):
                    product['category'] = details['category']
                
                parsed_products.append(product)
                time.sleep(0.5)
        
        time.sleep(1)
    
    # Children's shoes (no pagination)
    children_url = BASE_URLS["children"]
    logging.info(f"Парсинг детской обуви: {children_url}")
    
    html = fetch_html(children_url)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        
        cards = soup.select('.product-item, .product-card, .product, article.product, .item-product, [class*="product"]')
        
        if not cards:
            cards = soup.find_all('div', class_=re.compile('product|item', re.I))
        
        if cards:
            logging.info(f"Найдено {len(cards)} карточек на странице {children_url}")
            
            for card in cards:
                product = parse_product_card(card)
                if product and product.get('link'):
                    if product['link'] in seen_links:
                        continue
                    seen_links.add(product['link'])
                    
                    # Parse product details to get all images
                    details = parse_product_details(product['link'])
                    if details.get('images'):
                        product['images'] = details['images']
                    if details.get('category'):
                        product['category'] = details['category']
                    
                    parsed_products.append(product)
                    time.sleep(0.5)
    
    logging.info(f"✅ Salomon: всего собрано {len(parsed_products)} товаров")
    return parsed_products

