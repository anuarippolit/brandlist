import asyncio
import logging
from datetime import datetime
from parsers.superstep_scraper import parse_superstep
from parsers.fg_group_scraper import parse_fg_group
from parsers.club100_scraper import parse_club100
from parsers.allstars_scraper import parse_allstars
from parsers.adidas_scraper import parse_adidas
from parsers.salomon_scraper import parse_salomon
from utils.db_utils import save_products_to_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

async def run_scraper():
    """
    Запускает все парсеры для сбора информации о обуви с различных сайтов.
    Все парсеры работают параллельно в отдельных потоках.
    Сохраняет все товары в локальную базу данных.
    """
    start_time = datetime.now()
    logging.info("=" * 80)
    logging.info("🚀 ЗАПУСК СКРАПЕРА - Парсинг всех сайтов")
    logging.info("=" * 80)
    
    # Запускаем все парсеры параллельно
    futures = [
        asyncio.to_thread(parse_superstep),
        asyncio.to_thread(parse_fg_group),
        asyncio.to_thread(parse_club100),
        asyncio.to_thread(parse_allstars),
        asyncio.to_thread(parse_adidas),
        asyncio.to_thread(parse_salomon),
    ]

    parser_names = ["SuperStep", "FG Group", "Club100", "All-Stars", "Adidas", "Salomon"]
    
    logging.info(f"📡 Запущено {len(parser_names)} парсеров параллельно...")
    
    # Ждем завершения всех парсеров
    results = await asyncio.gather(*futures, return_exceptions=True)

    # Объединяем результаты и обрабатываем ошибки
    all_products = []
    successful_parsers = 0
    failed_parsers = 0
    
    logging.info("\n" + "=" * 80)
    logging.info("📊 РЕЗУЛЬТАТЫ ПАРСИНГА")
    logging.info("=" * 80)
    
    for i, result in enumerate(results):
        parser_name = parser_names[i]
        if isinstance(result, Exception):
            logging.error(f"❌ {parser_name}: Ошибка - {result}")
            failed_parsers += 1
        elif isinstance(result, list):
            all_products.extend(result)
            logging.info(f"✅ {parser_name}: собрано {len(result)} товаров")
            successful_parsers += 1
        else:
            logging.warning(f"⚠️ {parser_name}: неожиданный результат - {type(result)}")
            failed_parsers += 1

    # Унифицируем структуру продуктов
    logging.info("\n" + "=" * 80)
    logging.info("🔄 ОБРАБОТКА ДАННЫХ")
    logging.info("=" * 80)
    
    transformed = []
    skipped = 0
    
    for p in all_products:
        # Пропускаем товары без обязательных полей
        if not p.get("link") or not p.get("name"):
            skipped += 1
            continue
            
        # Обеспечиваем, что images - это список
        images = p.get("images", [])
        if isinstance(images, str):
            images = [images]
        elif not isinstance(images, list):
            images = []
        elif images is None:
            images = []

        transformed.append({
            "shop": p.get("shop", "Unknown"),
            "name": p.get("name", "No Name"),
            "images": images,
            "link": p.get("link", ""),
            "brand": p.get("brand"),
            "sale_price": p.get("sale_price") or p.get("price_discounted"),
            "first_price": p.get("first_price") or p.get("price_original"),
            "category": p.get("category", ["Обувь"]),
        })

    logging.info(f"📦 Всего товаров собрано: {len(all_products)}")
    logging.info(f"✅ Валидных товаров: {len(transformed)}")
    if skipped > 0:
        logging.warning(f"⚠️ Пропущено товаров (без link/name): {skipped}")

    # Сохраняем в базу данных
    if transformed:
        logging.info("\n" + "=" * 80)
        logging.info("💾 СОХРАНЕНИЕ В БАЗУ ДАННЫХ")
        logging.info("=" * 80)
        save_products_to_db(transformed)
    else:
        logging.warning("⚠️ Не удалось собрать товары для сохранения")

    # Итоговая статистика
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logging.info("\n" + "=" * 80)
    logging.info("📈 ИТОГОВАЯ СТАТИСТИКА")
    logging.info("=" * 80)
    logging.info(f"✅ Успешных парсеров: {successful_parsers}/{len(parser_names)}")
    logging.info(f"❌ Неудачных парсеров: {failed_parsers}/{len(parser_names)}")
    logging.info(f"📦 Всего товаров: {len(transformed)}")
    logging.info(f"⏱️ Время выполнения: {duration:.2f} секунд")
    logging.info("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_scraper())
