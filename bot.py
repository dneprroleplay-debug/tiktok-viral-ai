from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from groq import Groq
import asyncio
import json
import os

# =========================
# TOKENS
# =========================

BOT_TOKEN = "8854279157:AAGny_hfazw7DXKn9jo8-oARpIng6uXSuhc"

client = Groq(
    api_key="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"
)

ADMIN_ID = 805924502

# =========================
# BOT
# =========================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================
# FILES
# =========================

USERS_FILE = "users.json"

# =========================
# LOAD USERS
# =========================

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

users = load_users()

# =========================
# KEYBOARD
# =========================

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎬 Идея ролика"),
            KeyboardButton(text="🔥 Hook")
        ],
        [
            KeyboardButton(text="📈 Хештеги"),
            KeyboardButton(text="✍ Своя тема")
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
            "requests": 10
        }
        save_users(users)

    text = """
💎 PRO подписка

• Без лимитов
• Быстрые ответы
• Premium Hooks
• Viral сценарии
• Лучшие идеи для TikTok
"""

    await message.answer(text, reply_markup=menu)

# =========================
# IDEA
# =========================

@dp.message(F.text == "🎬 Идея ролика")
async def idea(message: Message):

    user_id = str(message.from_user.id)

    if users[user_id]["requests"] <= 0:
        await message.answer("❌ Лимит закончился")
        return

    users[user_id]["requests"] -= 1
    save_users(users)

    await message.answer("⏳ Генерирую идею...")

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "user",
                "content": "Придумай вирусную идею для TikTok"
            }
        ]
    )

    text = response.choices[0].message.content

    await message.answer(text)

# =========================
# HOOK
# =========================

@dp.message(F.text == "🔥 Hook")
async def hook(message: Message):

    user_id = str(message.from_user.id)

    if users[user_id]["requests"] <= 0:
        await message.answer("❌ Лимит закончился")
        return

    users[user_id]["requests"] -= 1
    save_users(users)

    await message.answer("⏳ Генерирую hook...")

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "user",
                "content": "Напиши мощный TikTok hook"
            }
        ]
    )

    text = response.choices[0].message.content

    await message.answer(text)

# =========================
# HASHTAGS
# =========================

@dp.message(F.text == "📈 Хештеги")
async def tags(message: Message):

    await message.answer(
        "#fyp #viral #tiktok #trend #reels #explore"
    )

# =========================
# OWN TOPIC
# =========================

@dp.message(F.text == "✍ Своя тема")
async def own(message: Message):

    await message.answer(
        "Напиши тему следующим сообщением"
    )

# =========================
# USER MESSAGE
# =========================

@dp.message()
async def all_messages(message: Message):

    user_id = str(message.from_user.id)

    if user_id not in users:
        users[user_id] = {
            "requests": 10
        }

    if users[user_id]["requests"] <= 0:
        await message.answer("❌ Лимит закончился")
        return

    users[user_id]["requests"] -= 1
    save_users(users)

    await message.answer("⏳ Думаю...")

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "user",
                "content": message.text
            }
        ]
    )

    text = response.choices[0].message.content

    await message.answer(text)

# =========================
# MAIN
# =========================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
