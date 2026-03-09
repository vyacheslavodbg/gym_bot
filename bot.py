import os
import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiohttp import web

# Ключ бот возьмет из настроек сервера сам
API_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# База данных
conn = sqlite3.connect('v_gym.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS logs (date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, text TEXT)')
conn.commit()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Слава, привет! Записывай тренировку. Например:\nБ Жим30 26 10 10 10")

@dp.message_handler()
async def save_log(message: types.Message):
    cursor.execute('INSERT INTO logs (text) VALUES (?)', (message.text,))
    conn.commit()
    await message.answer(f"✅ Принято: {message.text}")

async def handle(request):
    return web.Response(text="Bot is running")

async def on_startup(dispatcher):
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    asyncio.create_task(site.start())

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
