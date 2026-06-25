import asyncio
from app.bot import create_bot, create_dispatcher
from app.database import DataBase
from app.utils.functions import check_expired_groups
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)


async def main():
    bot = create_bot()
    dp = create_dispatcher()
    db = DataBase()
    await db.create_db()
    asyncio.create_task(check_expired_groups(bot))
    logging.info("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
