import asyncio
from parsers.lamoda_scraper import parse_lamoda_all
from parsers.fg_group_scraper import parse_fg_group
from utils.db_utils import save_products_to_db

async def run_scraper():
    # Запускаем оба парсера в отдельных потоках
    lamoda_future = asyncio.to_thread(parse_lamoda_all)
    fg_group_future = asyncio.to_thread(parse_fg_group)

    lamoda_raw, fg_raw = await asyncio.gather(lamoda_future, fg_group_future)

    all_products = lamoda_raw + fg_raw

    # Унифицируем структуру
    transformed = []
    for p in all_products:
        transformed.append({
            "shop": p.get("shop"),
            "name": p.get("name"),
            "colors": p.get("colors", []),
            "images": p.get("images", []),
            "link": p.get("link"),
            "sizes": p.get("sizes", []),
            "brand": p.get("brand"),
            "sale_price": p.get("sale_price"),
            "first_price": p.get("first_price"),
            "category": p.get("category", []),
            "gender": p.get("gender", []),
        })

    if transformed:
        save_products_to_db(transformed)

if __name__ == "__main__":
    asyncio.run(run_scraper())
