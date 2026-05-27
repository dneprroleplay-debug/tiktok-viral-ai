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
import random

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

FREE_LIMIT = 50

USERS_FILE = "users.json"
PRO_FILE = "pro_users.json"
REF_FILE = "refs.json"

busy_users = {}
waiting_custom_topic = set()

# =========================
# CREATE FILES
# =========================

for file_name, default_data in [
    (USERS_FILE, {}),
    (PRO_FILE, {}),
    (REF_FILE, {})
]:
    if not os.path.exists(file_name):
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(default_data, f)

# =========================
# LOAD
# =========================

with open(USERS_FILE, "r", encoding="utf-8") as f:
    user_limits = json.load(f)

with open(PRO_FILE, "r", encoding="utf-8") as f:
    pro_users = json.load(f)

with open(REF_FILE, "r", encoding="utf-8") as f:
    referrals = json.load(f)

# =========================
# SAVE
# =========================

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(user_limits, f, ensure_ascii=False, indent=4)

def save_pro():
    with open(PRO_FILE, "w", encoding="utf-8") as f:
        json.dump(pro_users, f, ensure_ascii=False, indent=4)

def save_refs():
    with open(REF_FILE, "w", encoding="utf-8") as f:
        json.dump(referrals, f, ensure_ascii=False, indent=4)

# =========================
# PRO CHECK
# =========================

def is_pro(user_id):

    user_id = str(user_id)

    if user_id not in pro_users:
        return False

    data = pro_users[user_id]

    if data == "forever":
        return True

    try:
        end_date = datetime.fromisoformat(data)

        if datetime.now() < end_date:
            return True

    except:
        pass

    del pro_users[user_id]
    save_pro()

    return False

# =========================
# PRO STATUS
# =========================

def get_pro_status(user_id):

    user_id = str(user_id)

    if user_id not in pro_users:
        return "❌ Нет"

    data = pro_users[user_id]

    if data == "forever":
        return "👑 Навсегда"

    try:
        end_date = datetime.fromisoformat(data)

        return f"💎 До {end_date.strftime('%d.%m.%Y')}"

    except:
        return "❌ Нет"

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

    if user_id not in user_limits:
        user_limits[user_id] = 0
        save_users()

    pro_status = get_pro_status(user_id)

    await message.answer(
        f"""
🚀 TikTok Viral AI 🚀

🔥 Бесплатный лимит:
{FREE_LIMIT} запросов

💎 PRO:
{pro_status}

Выбери что хочешь создать:
""",
        reply_markup=menu
    )

# =========================
# CALLBACKS
# =========================

@dp.callback_query()
async def callbacks(callback: CallbackQuery):

    user_id = str(callback.from_user.id)

    if callback.data == "buy_30":

        await callback.message.answer(
            f"""
💎 PRO 30 ДНЕЙ — $4.99

🆔 ID:
{user_id}

Напиши админу:
@keks77777
"""
        )

    elif callback.data == "buy_forever":

        await callback.message.answer(
            f"""
👑 PRO НАВСЕГДА — $14.99

🆔 ID:
{user_id}

Напиши админу:
@keks77777
"""
        )

    await callback.answer()

# =========================
# MAIN
# =========================

@dp.message()
async def generate(message: Message):

    user_id = str(message.from_user.id)
    current_text = message.text

    # =========================
    # ADMIN
    # =========================

    if message.from_user.id == ADMIN_ID:

        if current_text == "/stats":

            await message.answer(
                f"""
📊 СТАТИСТИКА

👥 Юзеров:
{len(user_limits)}

💎 PRO:
{len(pro_users)}

🔗 Рефералов:
{len(referrals)}
"""
            )

            return

    # =========================
    # REF
    # =========================

    if current_text == "👥 Рефералы":

        bot_info = await bot.get_me()

        link = f"https://t.me/{bot_info.username}?start={user_id}"

        await message.answer(
            f"""
👥 ТВОЯ ССЫЛКА

{link}

🎁 За друга:
+7 дней PRO
"""
        )

        return

    # =========================
    # PRO
    # =========================

    if current_text == "💎 PRO":

        pro_menu = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💎 PRO 30 ДНЕЙ",
                        callback_data="buy_30"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="👑 PRO НАВСЕГДА",
                        callback_data="buy_forever"
                    )
                ]
            ]
        )

        await message.answer(
            """
💎 TikTok Viral AI PRO

• Безлимит
• Лучшие Hooks
• Viral идеи
• Быстрые ответы
""",
            reply_markup=pro_menu
        )

        return

    # =========================
    # CUSTOM
    # =========================

    if current_text == "✍️ Своя тема":

        waiting_custom_topic.add(user_id)

        await message.answer(
            "✍️ Напиши тему"
        )

        return

    # =========================
    # LIMIT
    # =========================

    pro_status = is_pro(user_id)

    if not pro_status:

        if user_limits.get(user_id, 0) >= FREE_LIMIT:

            await message.answer(
                "❌ Лимит закончился"
            )

            return

    # =========================
    # BUSY
    # =========================

    if user_id in busy_users:

        await message.answer(
            "⏳ Подожди прошлый запрос"
        )

        return

    busy_users[user_id] = True

    try:

        # =========================
        # PROMPTS
        # =========================

        if current_text == "🎬 Идея ролика":

            prompt = """
Придумай 3 вирусные идеи для TikTok.

Формат:
🔥 HOOK
🎬 ИДЕЯ
📈 ХЕШТЕГИ
"""

        elif current_text == "🔥 Hook":

            prompt = """
Придумай 5 TikTok hooks.
"""

        elif current_text == "📈 Хештеги":

            prompt = """
Придумай вирусные TikTok хештеги.
"""

        elif user_id in waiting_custom_topic:

            waiting_custom_topic.remove(user_id)

            prompt = f"""
Придумай вирусный TikTok сценарий:

{current_text}
"""

        else:
            del busy_users[user_id]
            return

        # =========================
        # LOADING
        # =========================

        wait = await message.answer(
            random.choice([
                "⏳ Генерирую...",
                "🔥 Ищу тренды...",
                "🚀 Создаю контент..."
            ])
        )

        # =========================
        # AI
        # =========================

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=300
        )

        text = response.choices[0].message.content

        if not pro_status:
            user_limits[user_id] += 1
            save_users()

        left = FREE_LIMIT - user_limits[user_id]

        if pro_status:
            left_text = "♾ Безлимит"
        else:
            left_text = str(left)

        await wait.delete()

        await message.answer(
            f"""
━━━━━━━━━━━━━━━
🚀 TikTok Viral AI
━━━━━━━━━━━━━━━

{text}

━━━━━━━━━━━━━━━
📊 Осталось:
{left_text}
━━━━━━━━━━━━━━━
"""
        )

    except Exception as e:

        await message.answer(
            f"❌ Ошибка:\n{e}"
        )

    finally:

        if user_id in busy_users:
            del busy_users[user_id]

# =========================
# RUN
# =========================

async def main():

    print("BOT STARTED")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
