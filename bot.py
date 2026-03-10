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

# Подключение базы данных
conn = sqlite3.connect('v_gym.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS logs (date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, text TEXT)')
conn.commit()

# Настройка кнопок
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
btn_a = KeyboardButton('💪 Тренировка А')
btn_b = KeyboardButton('💪 Тренировка Б')
btn_stats = KeyboardButton('📊 Статистика')
btn_export = KeyboardButton('💾 Выгрузить CSV')

# Собираем клавиатуру: тренировки в один ряд, сервис в другой
keyboard.add(btn_a, btn_b)
keyboard.add(btn_stats, btn_export)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "Привет, Слава! Твой зал на связи.\n\n"
        "Выбирай программу ниже. Чтобы записать результат, просто отправь сообщение, например:\n"
        "'Жим 60 7 7 7 7'", 
        reply_markup=keyboard
    )

@dp.message_handler(lambda message: message.text == '💪 Тренировка А')
async def train_a(message: types.Message):
    plan_a = (
        "🏋️ **Тренировка А (База)**\n\n"
        "1. Жим штанги: 60 кг х 4 по 7\n"
        "2. Разгибания ног: 75 кг х 4 по 12\n"
        "3. Сгибания ног: 55 кг х 4 по 12\n"
        "4. Гравитрон (парал.): -20 кг х 4 по 8\n"
        "5. Брусья: св. вес х 4 по 10\n"
        "6. Бабочка: 50 кг х 4 по 12\n"
        "7. Молотки: 18 кг х 4 по 10\n"
        "8. Трицепс (блок): 30 кг х 4 по 12\n\n"
        "Жду результаты!"
    )
    await message.answer(plan_a, parse_mode="Markdown")

@dp.message_handler(lambda message: message.text == '💪 Тренировка Б')
async def train_b(message: types.Message):
    plan_b = (
        "🏋️ **Тренировка Б (Детали)**\n\n"
        "1. Жим гантелей 30°: 26 кг х 10 10 10 10\n"
        "2. Тяга гантели: 24 кг х 10 10 10 10\n"
        "3. Жим гантелей сидя: 16 кг х 10 10 10 8\n"
        "4. Обр. бабочка: 32 кг х 15 15 15 15\n"
        "5. Ноги (суперсет): х 12 12 12\n"
        "6. Икры: 60 кг х 15 15 15 15\n"
        "7. Скамья Скотта: 25 + гриф 9 9 9 8\n"
        "8. Трицепс (канат): 30 кг х 10 10 10 10\n\n"
        "Погнали!"
    )
    await message.answer(plan_b, parse_mode="Markdown")

@dp.message_handler(lambda message: message.text == '📊 Статистика')
async def show_stats(message: types.Message):
    cursor.execute('SELECT date, text FROM logs ORDER BY date DESC LIMIT 15')
    records = cursor.fetchall()
    if not records:
        await message.answer("В базе пока пусто.")
        return
    
    text = "📅 **Последние записи:**\n\n"
    for r in records:
        text += f"▪️ {r[0][5:16]} | {r[1]}\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message_handler(lambda message: message.text == '💾 Выгрузить CSV')
async def export_data(message: types.Message):
    cursor.execute("SELECT * FROM logs")
    rows = cursor.fetchall()
    with open("gym_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Дата", "Запись"])
        writer.writerows(rows)
    await message.answer_document(InputFile("gym_data.csv"), caption="Твои тренировки в файле.")

@dp.message_handler()
async def save_log(message: types.Message):
    cursor.execute('INSERT INTO logs (text) VALUES (?)', (message.text,))
    conn.commit()
    await message.answer(f"✅ Записал: {message.text}")

# Поддержка жизни на Render
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
