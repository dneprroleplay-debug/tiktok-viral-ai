from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from groq import Groq
import asyncio
import json
import os
from datetime import datetime, timedelta

# =========================
# TOKENS
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 805924502

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# =========================
# BOT
# =========================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================
# FILES
# =========================

USERS_FILE = "users.json"
PRO_FILE = "pro_users.json"

# =========================
# LOAD DATA
# =========================

def load_json(file_name, default):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(file_name, data):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

users = load_json(USERS_FILE, {})
pro_users = load_json(PRO_FILE, {})

# =========================
# MENU
# =========================

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎬 Идея ролика"),
            KeyboardButton(text="🔥 Hook")
        ],
        [
            KeyboardButton(text="📈 Хештеги"),
            KeyboardButton(text="✍️ Своя тема")
        ],
        [
            KeyboardButton(text="💎 PRO")
        ]
    ],
    resize_keyboard=True
)

# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):

    user_id = str(message.from_user.id)

    if user_id not in users:
        users[user_id] = {
            "requests": 50
        }

        save_json(USERS_FILE, users)

    pro_status = "✅ Да" if user_id in pro_users else "❌ Нет"

    text = f"""
🚀 ViralHook AI TikTok

🔥 Бесплатный лимит:
{users[user_id]['requests']} запросов

💎 PRO:
{pro_status}

Выбери что хочешь создать:
"""

    await message.answer(text, reply_markup=menu)

# =========================
# GENERATE
# =========================

async def generate_ai(prompt):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.9,
        max_tokens=700
    )

    return response.choices[0].message.content

# =========================
# BUTTONS
# =========================

@dp.message()
async def buttons(message: Message):

    user_id = str(message.from_user.id)

    if user_id not in users:
        users[user_id] = {
            "requests": 50
        }

    # ========= PRO =========

    if message.text == "💎 PRO":

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💎 PRO 30 дней — $5",
                        callback_data="buy_month"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="👑 PRO Навсегда — $15",
                        callback_data="buy_forever"
                    )
                ]
            ]
        )

        await message.answer(
            """
💎 PRO скоро будет доступен

• Без лимитов
• Быстрые ответы
• Premium hooks
• Viral сценарии
""",
            reply_markup=keyboard
        )

        return

    # ========= LIMIT =========

    if user_id not in pro_users:

        if users[user_id]["requests"] <= 0:
            await message.answer(
                "❌ Лимит закончился.\nКупи 💎 PRO"
            )
            return

        users[user_id]["requests"] -= 1
        save_json(USERS_FILE, users)

    await message.answer("⏳ Генерирую вирусный контент...")

    try:

        # ========= IDEA =========

        if message.text == "🎬 Идея ролика":

            prompt = """
Придумай вирусную идею TikTok ролика.
Кратко и красиво.
"""

        # ========= HOOK =========

        elif message.text == "🔥 Hook":

            prompt = """
Придумай 5 мощных TikTok Hook для вирусного видео.
"""

        # ========= TAGS =========

        elif message.text == "📈 Хештеги":

            prompt = """
Придумай вирусные TikTok хештеги.
"""

        # ========= CUSTOM =========

        else:

            prompt = f"""
Создай вирусный TikTok контент на тему:

{message.text}
"""

        text = await generate_ai(prompt)

        await message.answer(text[:4000])

    except Exception as e:

        await message.answer(
            f"❌ Ошибка:\n{e}"
        )

# =========================
# CALLBACKS
# =========================

@dp.callback_query()
async def callbacks(callback: CallbackQuery):

    if callback.data == "buy_month":

        await callback.message.answer(
            """
💎 PRO 30 дней — $5

Напиши админу:
@yourtelegram
"""
        )

    elif callback.data == "buy_forever":

        await callback.message.answer(
            """
👑 PRO Навсегда — $15

Напиши админу:
@yourtelegram
"""
        )

# =========================
# MAIN
# =========================

async def main():

    print("Бот запущен 🚀")

    await dp.start_polling(bot)

asyncio.run(main())
