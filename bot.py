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

BOT_TOKEN = "8854279157:AAGny_hfazw7DXKn9jo8-oARpIng6uXSuhc"

ADMIN_ID = 805924502

client = Groq(
    api_key="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"
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
            KeyboardButton(text="👥 Рефералы"),
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

        referrer_id = None

        args = message.text.split()

        if len(args) > 1:
            referrer_id = args[1]

users[user_id] = {
    "requests": 50
}

        if referrer_id and referrer_id != user_id:

            if referrer_id in users:

                users[referrer_id]["invited"] += 1

                if referrer_id not in pro_users:

                    pro_users[referrer_id] = {
                        "until": (
                            datetime.now() + timedelta(days=7)
                        ).strftime("%Y-%m-%d")
                    }

                save_json(PRO_FILE, pro_users)

        save_json(USERS_FILE, users)

    # ===== AUTO REMOVE EXPIRED PRO =====

    if user_id in pro_users:

        pro_data = pro_users[user_id]

        if "until" in pro_data:

            expire_date = datetime.strptime(
                pro_data["until"],
                "%Y-%m-%d"
            )

            if datetime.now() > expire_date:

                del pro_users[user_id]
                save_json(PRO_FILE, pro_users)

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
            "requests": 50,
            "invited": 0
        }

    # ================= PRO =================

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
💎 PRO подписка

• Без лимитов
• Быстрые ответы
• Premium Hooks
• Viral сценарии
• Лучшие идеи для TikTok
""",
            reply_markup=keyboard
        )

        return

    # ================= REF =================

    if message.text == "👥 Рефералы":

        bot_info = await bot.get_me()

        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"

        invited = users[user_id].get("invited", 0)

        await message.answer(
            f"""
👥 Реферальная система

Твоя ссылка:
{ref_link}

Приглашено друзей:
{invited}

🎁 За каждого друга:
+7 дней PRO
"""
        )

        return

    # ================= LIMIT =================

    if user_id not in pro_users:

        if users[user_id]["requests"] <= 0:

            await message.answer(
                "❌ Лимит закончился.\nКупи 💎 PRO"
            )

            return

        users[user_id]["requests"] -= 1

        save_json(USERS_FILE, users)

    await message.answer(
        "⏳ Генерирую вирусный контент..."
    )

    try:

        # ================= IDEA =================

        if message.text == "🎬 Идея ролика":

            prompt = """
Придумай вирусную идею TikTok ролика.
Сделай коротко и очень интересно.
"""

        # ================= HOOK =================

        elif message.text == "🔥 Hook":

            prompt = """
Придумай 5 мощных TikTok Hook
для вирусного видео.
"""

        # ================= TAGS =================

        elif message.text == "📈 Хештеги":

            prompt = """
Придумай вирусные TikTok хештеги
для больших просмотров.
"""

        # ================= CUSTOM =================

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
