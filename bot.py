import os
import sqlite3
import csv
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiohttp import web
import asyncio

API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# База данных
conn = sqlite3.connect('v_gym.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS logs (date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, text TEXT)')
conn.commit()

# Клавиатура
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton('📊 Статистика'), KeyboardButton('💾 Выгрузить CSV'))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Слава, пиши веса, я их сохраню. Статистику можно скачать файлом.", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == '📊 Статистика')
async def show_stats(message: types.Message):
    cursor.execute('SELECT date, text FROM logs ORDER BY date DESC LIMIT 10')
    records = cursor.fetchall()
    if not records:
        await message.answer("Записей пока нет.")
        return
    text = "\n".join([f"{r[0][:16]} | {r[1]}" for r in records])
    await message.answer(f"Последние 10 записей:\n{text}")

@dp.message_handler(lambda message: message.text == '💾 Выгрузить CSV')
async def export_data(message: types.Message):
    cursor.execute("SELECT * FROM logs")
    rows = cursor.fetchall()
    with open("gym_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Дата", "Запись"])
        writer.writerows(rows)
    await message.answer_document(InputFile("gym_data.csv"))

@dp.message_handler()
async def save_log(message: types.Message):
    cursor.execute('INSERT INTO logs (text) VALUES (?)', (message.text,))
    conn.commit()
    await message.answer(f"✅ Записал: {message.text}")

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
