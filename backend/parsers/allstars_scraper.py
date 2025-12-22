import requests
from bs4 import BeautifulSoup
import logging
from utils.db_utils import parse_price
import time
import json
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

URLS = {
    "https://all-stars.kz/store/men/shoes/": 20,
    "https://all-stars.kz/store/women/shoes/": 15,
    "https://all-stars.kz/store/deti/obuv/": 6,
}

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
        data_send = card.get('data-send', '')
        product_data = {}
        
        if data_send:
            try:
                product_data = json.loads(data_send)
            except:
                pass
        
        name = product_data.get('name', '')
        
        if not name:
            name_tag = card.select_one("a, h2, h3, .product-name, .s_item-title")
            if name_tag:
                name = name_tag.get_text(strip=True) or name_tag.get('title', '')
        
        if not name:
            return None

        link_tag = card.find('a', href=True)
        link = ""
        if link_tag:
            link = link_tag.get("href", "")
            if link and not link.startswith("http"):
                link = "https://all-stars.kz" + link

        brand = product_data.get('brand', '')
        if not brand:
            name_lower = name.lower()
            if "jordan" in name_lower:
                brand = "Jordan"
            elif "nike" in name_lower:
                brand = "Nike"
            elif "converse" in name_lower:
                brand = "Converse"
            elif "adidas" in name_lower:
                brand = "Adidas"
            else:
                brand = name.split()[0] if name else "Unknown Brand"

        sale_price = parse_price(product_data.get('price', ''))
        first_price = parse_price(product_data.get('oldPrice', ''))
        
        if not sale_price:
            price_tag = card.select_one(".price, .product-price, [class*='price']")
            if price_tag:
                price_text = price_tag.get_text(strip=True)
                sale_price = parse_price(price_text)
        
        if not first_price:
            old_price_tag = card.select_one(".old-price, .price-old, del")
            if old_price_tag:
                first_price = parse_price(old_price_tag.get_text(strip=True))
            else:
                first_price = sale_price

        images = []
        img_tags = card.find_all('img')
        for img_tag in img_tags:
            img_src = img_tag.get("src") or img_tag.get("data-src") or img_tag.get("data-lazy-src") or img_tag.get("data-original")
            if img_src:
                img_src_lower = img_src.lower()
                if ("data:image" in img_src_lower or "base64" in img_src_lower or 
                    "1x1" in img_src_lower or "placeholder" in img_src_lower or
                    "spacer" in img_src_lower or "blank" in img_src_lower):
                    continue
                if img_src not in images:
                    if not img_src.startswith("http"):
                        img_src = "https://all-stars.kz" + img_src
                    img_src = img_src.split("?")[0].split("&")[0]
                    if img_src and ("." in img_src[-5:] or "/" in img_src):
                        images.append(img_src)
        
        category = ["Обувь"]

        return {
            "shop": "All-Stars",
            "name": name,
            "brand": brand,
            "link": link,
            "images": images if images else [],
            "first_price": first_price or 0,
            "sale_price": sale_price or first_price or 0,
            "category": category,
        }
    except Exception as e:
        logging.warning(f"Ошибка парсинга карточки: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_product_details(product_url):
    html = fetch_html(product_url)
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")

    images = []
    gallery_containers = soup.select(".product-gallery, .product-images, .slick-slide, .swiper-slide")
    
    if gallery_containers:
        for container in gallery_containers:
            picture_elements = container.find_all("picture")
            for picture in picture_elements:
                source = picture.find("source", type="image/webp")
                if source and source.get("srcset"):
                    img_src = source.get("srcset").split()[0]
                    if img_src:
                        img_src_lower = img_src.lower()
                        if ("iblock" in img_src_lower and "logo" not in img_src_lower and
                            "icon" not in img_src_lower and "delivery" not in img_src_lower and
                            "preview" not in img_src_lower):
                            if not img_src.startswith("http"):
                                img_src = "https://all-stars.kz" + img_src
                            img_src = img_src.split("?")[0].split("&")[0]
                            if "457_457_1" in img_src and img_src not in images:
                                images.append(img_src)
                            continue
                
                img = picture.find("img")
                if img:
                    img_src = img.get("data-src") or img.get("src")
                    if img_src:
                        img_src_lower = img_src.lower()
                        if ("iblock" in img_src_lower and "logo" not in img_src_lower and
                            "icon" not in img_src_lower and "delivery" not in img_src_lower and
                            "preview" not in img_src_lower and
                            "data:image" not in img_src_lower and "base64" not in img_src_lower):
                            if not img_src.startswith("http"):
                                img_src = "https://all-stars.kz" + img_src
                            img_src = img_src.split("?")[0].split("&")[0]
                            if "457_457_1" in img_src and img_src not in images:
                                images.append(img_src)
    
    if not images:
        picture_elements = soup.find_all("picture")
        for picture in picture_elements:
            parent_classes = []
            parent = picture.find_parent()
            while parent and len(parent_classes) < 3:
                if parent.get("class"):
                    parent_classes.extend(parent.get("class", []))
                parent = parent.find_parent()
            
            parent_classes_str = " ".join(parent_classes).lower()
            if any(word in parent_classes_str for word in ["header", "footer", "nav", "menu", "logo"]):
                continue
            
            source = picture.find("source", type="image/webp")
            if source and source.get("srcset"):
                img_src = source.get("srcset").split()[0]
                if img_src:
                    img_src_lower = img_src.lower()
                    if ("iblock" in img_src_lower and "457_457_1" in img_src_lower and
                        "logo" not in img_src_lower and "icon" not in img_src_lower and
                        "preview" not in img_src_lower):
                        if not img_src.startswith("http"):
                            img_src = "https://all-stars.kz" + img_src
                        img_src = img_src.split("?")[0].split("&")[0]
                        if img_src not in images:
                            images.append(img_src)

    categories = ["Обувь"]
    breadcrumb_tags = soup.select(".breadcrumb a, .breadcrumbs a, .breadcrumb-list a")
    filtered_breadcrumbs = []
    for crumb in breadcrumb_tags:
        crumb_text = crumb.get_text(strip=True)
        if crumb_text and crumb_text.lower() not in ["главная", "home", "каталог", "catalog", "магазин", "shop", "store"]:
            filtered_breadcrumbs.append(crumb_text)
    
    if len(filtered_breadcrumbs) >= 2:
        category_text = filtered_breadcrumbs[-2]
        if category_text not in categories:
            categories.append(category_text)
    elif len(filtered_breadcrumbs) == 1:
        if filtered_breadcrumbs[0] not in categories:
            categories.append(filtered_breadcrumbs[0])

    return {
        "images": images if images else None,
        "category": categories
    }

def parse_allstars():
    parsed_products = []

    for base_url, max_pages in URLS.items():
        seen_links = set()
        is_kids = "/deti/obuv/" in base_url
        
        for page in range(1, max_pages + 1):
            if is_kids:
                url = f"{base_url}?PAGEN_2={page}&clear_cache=Y"
            elif page == 1:
                url = base_url
            else:
                url = f"{base_url}?PAGEN_2={page}&clear_cache=Y"
            
            html = fetch_html(url)
            if not html:
                logging.warning(f"Не удалось получить HTML для страницы {page}, пропускаем")
                continue

            soup = BeautifulSoup(html, "html.parser")
        
            card_selectors = [
                "article.s_item",
                "article[data-send]",
                "article",
            ]
        
            cards = []
            for selector in card_selectors:
                cards = soup.select(selector)
                if cards:
                    break

            if not cards:
                logging.info(f"Не найдены карточки товаров на странице {page}, пропускаем")
                continue

            logging.info(f"Страница {page}/{max_pages}: найдено {len(cards)} карточек")

            for card in cards:
                product = parse_product_card(card)
                if product and product.get("link"):
                    if product["link"] in seen_links:
                        continue
                    seen_links.add(product["link"])
                    card_images = product.get("images", [])
                    details = parse_product_details(product["link"])
                    if details.get("images") and len(details["images"]) > 0:
                        product["images"] = details["images"]
                    elif not product.get("images") or len(product.get("images", [])) == 0:
                        product["images"] = card_images if card_images else []
                    if details.get("category"):
                        product["category"] = details["category"]
                    parsed_products.append(product)
                time.sleep(1)

    logging.info(f"✅ All-Stars: всего собрано {len(parsed_products)} товаров")
    return parsed_products

if __name__ == "__main__":
    all_products = parse_allstars()
    print(f"🧪 Всего товаров: {len(all_products)}")
    for product in all_products[:3]:
        print("\n" + "-" * 60)
        for key, val in product.items():
            print(f"{key}: {val}")
