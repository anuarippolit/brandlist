import requests
from bs4 import BeautifulSoup
import logging
from utils.db_utils import parse_price
import time
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "https://superstep.kz/catalog/{category}-{sub_category}/?PAGEN_1={page}&bxajaxid=32ff20c93ce0fdbe79535b1238d9b6c9"
CATEGORIES = ["muzhchiny"]
SUB_CATEGORIES = ["obuv"]
MAX_PAGES = 1000

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_html(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        time.sleep(5)
        return None

def parse_product_card(card):
    try:
        name_tag = card.select_one(".product-name a")
        raw_name = name_tag.get_text(separator=" ", strip=True) if name_tag else "No Name"
        link = "https://superstep.kz" + name_tag['href'] if name_tag else "No Link"

        brand_meta = card.select_one("meta[itemprop='brand']")
        brand = brand_meta["content"] if brand_meta else "Unknown Brand"

        name = raw_name
        name = name.replace("Мужская обувь", "").replace("Женская обувь", "").replace("Детская обувь", "").strip()
        if brand and name.startswith(brand.upper()):
            name = name[len(brand.upper()):].strip()
        if brand and name.endswith(brand.upper()):
            name = name[:-len(brand.upper())].strip()
        name = " ".join(name.split())
        if not name:
            name = raw_name
        if brand and brand.upper() not in name.upper():
            name = f"{name} {brand}".strip()

        prices = card.select(".product-double-price span")
        first_price_raw = parse_price(prices[0].get_text(strip=True)) if len(prices) > 0 else None
        sale_price_raw = parse_price(prices[1].get_text(strip=True)) if len(prices) > 1 else None

        if sale_price_raw and first_price_raw and sale_price_raw < first_price_raw:
            first_price_value = first_price_raw
            sale_price_value = sale_price_raw
        else:
            first_price_value = first_price_raw
            sale_price_value = None
        image_tag = card.select_one(".product-item-image_first")
        main_image = "https://superstep.kz" + image_tag['src'] if image_tag and image_tag.get('src') else None
        images = [main_image] if main_image else []

        return {
            "shop": "SuperStep",
            "name": name,
            "brand": brand,
            "link": link,
            "images": images,
            "first_price": first_price_value,
            "sale_price": sale_price_value,
            "category": ["Обувь"],
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
    script_tags = soup.find_all("script")
    logging.info(f"Проверяем {len(script_tags)} script тегов на наличие изображений")
    for script in script_tags:
        script_content = script.string or ""
        if not script_content:
            continue
        
        image_urls = re.findall(r'["\']([^"\']*iblock[^"\']*\.(jpg|jpeg|png|webp))["\']', script_content, re.IGNORECASE)
        for url_match, ext in image_urls:
            if "/uf/" not in url_match.lower() and "banner" not in url_match.lower() and "noimage" not in url_match.lower():
                url_match = url_match.replace("\\/", "/")
                if not url_match.startswith("http"):
                    url_match = "https://superstep.kz" + url_match
                url_match = url_match.split("?")[0]
                url_match = re.sub(r'/\d+_\d+_\d+/', '/800_800_2/', url_match)
                base_match = re.search(r'/([^/]+\.(jpg|jpeg|png|webp))$', url_match, re.IGNORECASE)
                if base_match:
                    base_filename = base_match.group(1)
                    existing_base = any(base_filename in img for img in images)
                    if not existing_base:
                        images.append(url_match)
        
        json_matches = re.findall(r'["\'](?:images|gallery|photos|pictures)["\']\s*:\s*\[(.*?)\]', script_content, re.DOTALL)
        for json_array in json_matches:
            urls = re.findall(r'["\']([^"\']*iblock[^"\']*\.(jpg|jpeg|png|webp))["\']', json_array, re.IGNORECASE)
            for url_match, ext in urls:
                if "/uf/" not in url_match.lower() and "noimage" not in url_match.lower():
                    url_match = url_match.replace("\\/", "/")
                    if not url_match.startswith("http"):
                        url_match = "https://superstep.kz" + url_match
                    url_match = url_match.split("?")[0]
                    url_match = re.sub(r'/\d+_\d+_\d+/', '/800_800_2/', url_match)
                    base_match = re.search(r'/([^/]+\.(jpg|jpeg|png|webp))$', url_match, re.IGNORECASE)
                    if base_match:
                        base_filename = base_match.group(1)
                        existing_base = any(base_filename in img for img in images)
                        if not existing_base:
                            images.append(url_match)
    all_elements_with_data = soup.find_all(attrs={"data-src": True}) + soup.find_all(attrs={"data-images": True}) + soup.find_all(attrs={"data-gallery": True})
    for elem in all_elements_with_data:
        data_src = elem.get("data-src") or elem.get("data-images") or elem.get("data-gallery")
        if data_src and "iblock" in data_src.lower() and "/uf/" not in data_src.lower():
            if not data_src.startswith("http"):
                data_src = "https://superstep.kz" + data_src
            data_src = data_src.split("?")[0]
            data_src = re.sub(r'/\d+_\d+_\d+/', '/800_800_2/', data_src)
            if data_src not in images:
                images.append(data_src)
    
    slider_items = soup.select(".product-slider__main")
    for item in slider_items:
        for attr_name, attr_value in item.attrs.items():
            if attr_name.startswith("data-") and isinstance(attr_value, str):
                if "iblock" in attr_value.lower() and "/uf/" not in attr_value.lower() and "noimage" not in attr_value.lower():
                    if not attr_value.startswith("http"):
                        attr_value = "https://superstep.kz" + attr_value
                    attr_value = attr_value.split("?")[0]
                    attr_value = re.sub(r'/\d+_\d+_\d+/', '/800_800_2/', attr_value)
                    if attr_value not in images:
                        images.append(attr_value)
    
    slick_track = soup.select_one(".slick-track")
    if slick_track:
        slider_items = slick_track.select(".product-slider__main")
        for item in slider_items:
            img = item.find("img", class_="product-slider__img")
            if img:
                img_src = img.get("src")
                if img_src:
                    img_src_lower = img_src.lower()
                    if ("noimage" in img_src_lower or "placeholder" in img_src_lower or 
                        "/uf/" in img_src_lower or "banner" in img_src_lower or
                        "menu" in img_src_lower or "logo" in img_src_lower):
                        continue
                    if "iblock" not in img_src_lower:
                        continue
                    if img_src.startswith("http"):
                        full_url = img_src
                    else:
                        full_url = "https://superstep.kz" + img_src
                    full_url = full_url.split("?")[0]
                    full_url = re.sub(r'/\d+_\d+_\d+/', '/800_800_2/', full_url)
                    if full_url not in images:
                        images.append(full_url)
    
    slider_items = soup.select(".product-slider__main")
    for item in slider_items:
        orig = item.get("orig")
        if orig:
            orig = re.sub(r'/\d+_\d+_\d+/', '/800_800_2/', orig)
            if not orig.startswith("http"):
                orig = "https://superstep.kz" + orig
            if orig not in images and "iblock" in orig.lower() and "/uf/" not in orig.lower():
                images.append(orig)
                continue
        
        img = item.find("img", class_=re.compile("product-slider__img"))
        if not img:
            img = item.find("img")
        if img:
            img_src = (img.get("src") or img.get("data-src") or 
                      img.get("data-lazy-src") or img.get("data-original") or
                      img.get("data-zoom-image"))
            if img_src and "iblock" in img_src.lower() and "/uf/" not in img_src.lower() and "noimage" not in img_src.lower():
                if not img_src.startswith("http"):
                    img_src = "https://superstep.kz" + img_src
                img_src = img_src.split("?")[0]
                img_src = re.sub(r'/\d+_\d+_\d+/', '/800_800_2/', img_src)
                if img_src not in images:
                    images.append(img_src)
    
    if not images:
        image_selectors = [
            ".product-slider__thumbnail-img img",
            ".product-images img",
            ".product-gallery img",
        ]
        for selector in image_selectors:
            image_tags = soup.select(selector)
            for img in image_tags:
                img_src = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or img.get("data-zoom-image") or img.get("data-original")
                if img_src:
                    img_src_lower = img_src.lower()
                    if ("noimage" in img_src_lower or "placeholder" in img_src_lower or 
                        "/uf/" in img_src_lower or "banner" in img_src_lower or
                        "menu" in img_src_lower or "logo" in img_src_lower):
                        continue
                    if "iblock" not in img_src_lower:
                        continue
                    if img_src.startswith("http"):
                        full_url = img_src
                    else:
                        full_url = "https://superstep.kz" + img_src
                    full_url = full_url.split("?")[0]
                    full_url = re.sub(r'/\d+_\d+_\d+/', '/800_800_2/', full_url)
                    if full_url not in images:
                        images.append(full_url)
            if images:
                break
    
    if not images:
        all_imgs = soup.find_all("img", src=True)
        for img in all_imgs:
            img_src = img.get("src")
            if img_src:
                img_src_lower = img_src.lower()
                if ("iblock" in img_src_lower and "noimage" not in img_src_lower and
                    "/uf/" not in img_src_lower and "banner" not in img_src_lower):
                    if not img_src.startswith("http"):
                        img_src = "https://superstep.kz" + img_src
                    img_src = img_src.split("?")[0]
                    img_src = re.sub(r'/\d+_\d+_\d+/', '/800_800_2/', img_src)
                    if img_src not in images:
                        images.append(img_src)

    categories = ["Обувь"]
    breadcrumb = soup.select_one(".breadcrumb:not(nav .breadcrumb), .breadcrumbs:not(nav .breadcrumbs), .breadcrumb-nav:not(nav .breadcrumb-nav)")
    if breadcrumb:
        breadcrumb_links = breadcrumb.select("a")
        valid_categories = []
        for cat_tag in breadcrumb_links:
            cat_text = cat_tag.get_text(strip=True)
            exclude_words = [
                "главная", "home", "каталог", "catalog", "магазин", "shop",
                "мужчинам", "женщинам", "детям", "смотреть всё", "смотреть всёсмотреть всё",
                "поло", "carhartt", "шапки", "кепки", "adidas", "tommy", "jeans", "alpha",
                "industries", "skechers", "calvin", "klein", "брюки", "шорты", "hugo", "red",
                "emu", "платья", "юбки", "все бренды", "толстовки", "helly", "hansen",
                "рубашки", "jack", "wolfskin", "lacoste", "primitive", "sale", "футболки",
                "new balance", "reebok", "нижнее белье", "crocs", "jansport", "одежда",
                "the hundreds", "merrell", "anta", "hilfiger", "karl", "kani", "market",
                "новинки", "куртки", "puma", "les benjamins", "champion", "herschel",
                "последний размер", "детям", "кепки", "мужская одежда", "дети", "спортивные брюки",
                "женщины", "заполнить форму", "сланцы", "мужчины", "timberland", "носки",
                "jordan", "наша почта", "мужские", "8 800", "huf",
                "спортивный костюм", "united 4", "бренды", "the north face", "магазины",
                "кеды", "ugg", "vans", "женщинам", "hugo blue", "premium", "все контакты",
                "nike", "converse", "returns", "info", "сумки", "обувь и аксессуары", "мужская обувь", "женская обувь"
            ]
            if (cat_text and 
                len(cat_text) < 30 and 
                cat_text.lower() not in [w.lower() for w in exclude_words] and
                cat_text not in valid_categories):
                if "@" not in cat_text and not any(char.isdigit() for char in cat_text[:2]):
                    valid_categories.append(cat_text)
        
        specific_categories = [c for c in valid_categories if c.lower() in ["кроссовки", "ботинки", "кеды", "сапоги", "тапочки", "мужские ботинки", "женские ботинки"]]
        if specific_categories:
            categories = ["Обувь"] + specific_categories
        elif valid_categories:
            categories = ["Обувь"] + [valid_categories[-1]]
    
    if len(categories) == 1:
        product_cat_tags = soup.select(".detail__info-wrapper .product-category, .product-category")
        for cat_tag in product_cat_tags:
            cat_text = cat_tag.get_text(strip=True)
            if cat_text and cat_text.lower() in ["кроссовки", "ботинки", "кеды", "сапоги", "тапочки"]:
                if cat_text not in categories:
                    categories.append(cat_text)

    return {
        "images": images if images else None,
        "category": list(set(categories))
    }

def parse_superstep():
    parsed_products = []

    for category in CATEGORIES:
        for sub_category in SUB_CATEGORIES:
            page = 1
            seen_links = set()
            
            while True:
                if page > MAX_PAGES:
                    logging.warning(f"Достигнут лимит {MAX_PAGES} страниц для {category}/{sub_category}, останавливаемся")
                    break
                    
                url = BASE_URL.format(category=category, sub_category=sub_category, page=page)
                html = fetch_html(url)
                if not html:
                    logging.warning(f"Не удалось получить HTML для страницы {page}, останавливаемся")
                    break

                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select(".product-item-wrapper")
                
                if not cards:
                    logging.info(f"[{category}/{sub_category}] Страница {page}: товары не найдены, парсинг завершен")
                    break
                
                logging.info(f"[{category}/{sub_category}] Страница {page}: найдено {len(cards)} карточек")

                for card in cards:
                    product = parse_product_card(card)
                    if product:
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

    logging.info(f"✅ SuperStep: всего собрано {len(parsed_products)} товаров")
    return parsed_products
