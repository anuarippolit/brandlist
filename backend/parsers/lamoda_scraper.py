# # import requests
# # import logging
# #
# # # Настройка логирования
# # logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# #
# # LAMODA_URLS = [
# #     {
# #         "base_url": "https://www.lamoda.kz/c/355/clothes-zhenskaya-odezhda/",
# #         "params": "?sitelink=topmenuW&l=2&page=",
# #         "json_param": "&json=1",
# #         "category": "Одежда",
# #     }
# # ]
# #
# # PAGE_LIMIT = 2  # Количество страниц для парсинга
# #
# # def fetch_json(url):
# #     """Делает GET-запрос и возвращает JSON."""
# #     try:
# #         response = requests.get(url, timeout=10)
# #         response.raise_for_status()
# #         return response.json()
# #     except requests.exceptions.RequestException as e:
# #         logging.error(f"Ошибка запроса: {e}")
# #         return None
# #
# # def parse_product(product, category):
# #     """Извлекает информацию о продукте."""
# #     parsed_products = []
# #
# #     product_name = product.get("name", "No Name")
# #     brand = product.get("brand", {}).get("name", "Unknown Brand")
# #     sku = product.get("sku", "Unknown SKU")
# #     seo_tail = product.get("seo_tail", "")
# #     product_link = f"https://www.lamoda.kz/p/{sku}/{seo_tail}/"
# #
# #     # Изображение
# #     image_url = product.get("gallery", [None])[0]
# #     image_url = f"https://a.lmcdn.ru/img600x866{image_url}" if image_url else "No Image"
# #
# #     # Доступные размеры
# #     sizes = [size.get("size", "") for size in product.get("sizes", []) if size.get("is_available", False)]
# #
# #     # Цены
# #     prices = product.get("prices", [])
# #     first_price = prices[0].get("price", 0) if prices else 0
# #     sale_price = prices[-1].get("price", 0) if prices else 0
# #
# #     # Категории
# #     categories = [category, product_name.split(" ")[0]]
# #
# #     # Цвета
# #     colors = product.get("colors", {})
# #
# #     for color_name in colors.values():
# #         parsed_products.append({
# #             "shop": "Lamoda",
# #             "name": product_name,
# #             "color": color_name,
# #             "image_url": image_url,
# #             "link": product_link,
# #             "sizes": sizes,
# #             "brand": brand,
# #             "sale_price": sale_price,
# #             "first_price": first_price,
# #             "category": categories,
# #         })
# #
# #     return parsed_products
# #
# # def parse_lamoda():
# #     """Парсит сайт Lamoda и возвращает список товаров."""
# #     parsed_products = []
# #
# #     for source in LAMODA_URLS:
# #         base_url = source["base_url"]
# #         params = source["params"]
# #         json_param = source["json_param"]
# #         category = source["category"]
# #
# #         for page in range(1, PAGE_LIMIT + 1):
# #             url = f"{base_url}{params}{page}{json_param}"
# #
# #             data = fetch_json(url)
# #             if not data:
# #                 logging.warning(f"Не удалось получить данные с {url}")
# #                 continue
# #
# #             products = data.get("payload", {}).get("products", [])
# #             if not products:
# #                 logging.info(f"На странице {page} нет товаров")
# #                 continue
# #
# #             for product in products:
# #                 parsed_products.extend(parse_product(product, category))
# #
# #     return parsed_products
#
# import requests
# from urllib.parse import urlparse
#
# LAMODA_LINKS = [
#     (["man"], "https://www.lamoda.kz/c/477/clothes-muzhskaya-odezhda/", "Одежда"),
#     (["man"], "https://www.lamoda.kz/c/17/shoes-men/", "Обувь"),
#     (["man"], "https://www.lamoda.kz/c/559/accs-muzhskieaksessuary/", "Аксессуары"),
#     (["woman"], "https://www.lamoda.kz/c/355/clothes-zhenskaya-odezhda/", "Одежда"),
#     (["woman"], "https://www.lamoda.kz/c/15/shoes-women/", "Обувь"),
#     (["woman"], "https://www.lamoda.kz/c/557/accs-zhenskieaksessuary/", "Аксессуары"),
#     (["kid", "girl"], "https://www.lamoda.kz/c/5379/default-devochkam/?genders=girls", "Для девочек"),
#     (["kid", "boy"], "https://www.lamoda.kz/c/5378/default-malchikam/", "Для мальчиков"),
#     (["kid", "newborn"], "https://www.lamoda.kz/c/5414/default-novorozhdennym/", "Для новорожденных"),
# ]
#
# def fetch_json(url):
#     try:
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()
#         return response.json()
#     except:
#         return None
#
# def parse_product_grouped(product, gender_list, category, by_link):
#     product_name = product.get("name", "")
#     brand = product.get("brand", {}).get("name", "")
#     sku = product.get("sku", "")
#     seo_tail = product.get("seo_tail", "")
#     product_link = f"https://www.lamoda.kz/p/{sku}/{seo_tail}/"
#
#     gallery = product.get("gallery", [])
#     image_urls = [f"https://a.lmcdn.ru/img600x866{img}" for img in gallery[:5]]
#
#     sizes = [size.get("size", "") for size in product.get("sizes", []) if size.get("is_available", False)]
#
#     prices = product.get("prices", [])
#     first_price = prices[0].get("price", 0) if prices else 0
#     sale_price = prices[-1].get("price", 0) if prices else 0
#
#     colors = list(product.get("colors", {}).values())
#
#     if product_link in by_link:
#         by_link[product_link]["colors"].update(colors)
#     else:
#         by_link[product_link] = {
#             "shop": "Lamoda",
#             "name": product_name,
#             "colors": set(colors),
#             "images": image_urls,
#             "link": product_link,
#             "sizes": sizes,
#             "brand": brand,
#             "sale_price": sale_price,
#             "first_price": first_price,
#             "category": [category, product_name.split(" ")[0]],
#             "gender": gender_list,
#         }
#
# def parse_lamoda_all():
#     by_link = {}
#
#     for gender_list, base_url, category in LAMODA_LINKS:
#         page = 1
#         while True:
#             if "?" in base_url:
#                 full_url = f"{base_url}&page={page}&json=1"
#             else:
#                 full_url = f"{base_url}?page={page}&json=1"
#
#             data = fetch_json(full_url)
#             if not data:
#                 break
#
#             products = data.get("payload", {}).get("products", [])
#             if not products:
#                 break
#
#             for product in products:
#                 product_name = product.get("name", "")
#                 sku = product.get("sku", "")
#                 seo_tail = product.get("seo_tail", "")
#                 product_link = f"https://www.lamoda.kz/p/{sku}/{seo_tail}/"
#
#                 if product_link in by_link:
#                     new_colors = list(product.get("colors", {}).values())
#                     by_link[product_link]["colors"].update(new_colors)
#                 else:
#                     parse_product_grouped(product, gender_list, category, by_link)
#
#             page += 1
#
#     results = []
#     for product in by_link.values():
#         product["colors"] = list(product["colors"])
#         results.append(product)
#
#     return results

import requests
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

LAMODA_LINKS = [
    (["man"], "https://www.lamoda.kz/c/477/clothes-muzhskaya-odezhda/", "Одежда"),
    (["man"], "https://www.lamoda.kz/c/17/shoes-men/", "Обувь"),
    (["man"], "https://www.lamoda.kz/c/559/accs-muzhskieaksessuary/", "Аксессуары"),
    (["woman"], "https://www.lamoda.kz/c/355/clothes-zhenskaya-odezhda/", "Одежда"),
    (["woman"], "https://www.lamoda.kz/c/15/shoes-women/", "Обувь"),
    (["woman"], "https://www.lamoda.kz/c/557/accs-zhenskieaksessuary/", "Аксессуары"),
    (["kid", "girl"], "https://www.lamoda.kz/c/5379/default-devochkam/?genders=girls", "Для девочек"),
    (["kid", "boy"], "https://www.lamoda.kz/c/5378/default-malchikam/", "Для мальчиков"),
    (["kid", "newborn"], "https://www.lamoda.kz/c/5414/default-novorozhdennym/", "Для новорожденных"),
]

def fetch_json(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return None

def parse_product_grouped(product, gender_list, category, by_link):
    name = product.get("name", "").strip()
    brand = product.get("brand", {}).get("name", "").strip()
    model = product.get("model_name", "").strip()
    product_name = f"{name} {brand} {model}".strip()
    sku = product.get("sku", "")
    seo_tail = product.get("seo_tail", "")
    product_link = f"https://www.lamoda.kz/p/{sku}/{seo_tail}/"

    gallery = product.get("gallery", [])
    image_urls = [f"https://a.lmcdn.ru/img600x866{img}" for img in gallery[:5]]

    sizes = [size.get("size", "") for size in product.get("sizes", []) if size.get("is_available", False)]

    prices = product.get("prices", [])
    first_price = prices[0].get("price", 0) if prices else 0
    sale_price = prices[-1].get("price", 0) if prices else 0

    colors = list(product.get("colors", {}).values())

    if product_link in by_link:
        by_link[product_link]["colors"].update(colors)
    else:
        by_link[product_link] = {
            "shop": "Lamoda",
            "name": product_name,
            "colors": set(colors),
            "images": image_urls,
            "link": product_link,
            "sizes": sizes,
            "brand": brand,
            "sale_price": sale_price,
            "first_price": first_price,
            "category": [category, product_name.split(" ")[0]],
            "gender": gender_list,
        }

def parse_lamoda_all():
    by_link = {}

    for gender_list, base_url, category in LAMODA_LINKS:
        for page in range(1, 167):
            if "?" in base_url:
                full_url = f"{base_url}&page={page}&json=1"
            else:
                full_url = f"{base_url}?page={page}&json=1"

            data = fetch_json(full_url)
            if not data:
                break

            products = data.get("payload", {}).get("products", [])
            logging.info(f"[{category}] страница {page}: найдено {len(products)} товаров")

            if not products:
                break

            for product in products:
                product_name = product.get("name", "")
                sku = product.get("sku", "")
                seo_tail = product.get("seo_tail", "")
                product_link = f"https://www.lamoda.kz/p/{sku}/{seo_tail}/"

                if product_link in by_link:
                    new_colors = list(product.get("colors", {}).values())
                    by_link[product_link]["colors"].update(new_colors)
                else:
                    parse_product_grouped(product, gender_list, category, by_link)

            page += 1

    results = []
    for product in by_link.values():
        product["colors"] = list(product["colors"])
        results.append(product)

    return results
