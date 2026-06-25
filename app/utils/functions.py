import asyncio
import time
import aiohttp
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database import DataBase
database = DataBase()

async def add_group_db(chat_id, interval, name):
    db = await database.connect_db()
    next_send_at = int(time.time()) + int(interval) * 60
    await db.execute("INSERT INTO groups (chat_id, interval_minutes, name, next_send_at) VALUES (?,?,?,?)",
                     (chat_id, interval, name, next_send_at,))
    await database.close_db()


async def delete_from_db(chat_id):
    db = await database.connect_db()
    await db.execute("DELETE FROM groups WHERE chat_id = (?)", (chat_id,))
    await database.close_db()


async def get_removedb_keyb():
    db = await database.connect_db()
    cur = await db.execute("SELECT name, chat_id FROM groups")
    cur = await cur.fetchall()
    keyb = InlineKeyboardBuilder()
    await database.close_db()
    for name, chat_id in cur:
        keyb.add(InlineKeyboardButton(text=name, callback_data=f'removegroup_{chat_id}'))
    keyb.add(InlineKeyboardButton(text='◀ Назад', callback_data='back'))
    keyb.adjust(1)
    return keyb.as_markup()


def back_keyb():
    keyb = InlineKeyboardBuilder()
    keyb.add(InlineKeyboardButton(text='◀ Назад', callback_data='back'))
    return keyb.as_markup()


async def get_btc_price():
    async with aiohttp.ClientSession() as ses:
        usd = await ses.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
        usd_data = await usd.json()
        rub = await ses.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCRUB")
        rub_data = await rub.json()

    btc_usd = float(usd_data["price"])
    btc_rub = float(rub_data["price"])
    return (f"📊 Текущий курс <b>BTC</b>\n\n"
            f"BTC/USD: ${btc_usd}\n"
            f"BTC/RUB: ₽{btc_rub}")


async def check_expired_groups(bot):
    while True:
        db = await database.connect_db()
        now = int(time.time())
        cur = await db.execute(
            "SELECT ID, chat_id, name, interval_minutes "
            "FROM groups WHERE next_send_at <= ?", (now,))
        groups = await cur.fetchall()
        for ids, chat_id, name, interval in groups:
            text = await get_btc_price()
            await bot.send_message(chat_id=chat_id, text=text)
            await db.execute("UPDATE groups SET next_send_at = ? WHERE ID = ?", (now + interval * 60, ids))
        await database.close_db()
        await asyncio.sleep(30)
