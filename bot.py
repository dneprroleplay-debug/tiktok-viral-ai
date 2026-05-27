```python
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from openai import OpenAI

import asyncio
import json
import os
import random

from datetime import datetime, timedelta

# =========================
# TOKENS
# =========================

BOT_TOKEN = "8854279157:AAGny_hfazw7DXKn9jo8-oARpIng6uXSuhc"

ADMIN_ID = 805924502

client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
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
# LOAD JSON
# =========================

def load_json(path, default):

    if os.path.exists(path):

        try:

            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)

        except:
            return default

    return default

# =========================
# SAVE JSON
# =========================

def save_json(path, data):

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )

# =========================
# DATABASES
# =========================

user_limits = load_json(USERS_FILE, {})
pro_users = load_json(PRO_FILE, {})
referrals = load_json(REF_FILE, {})

# =========================
# SAVE FUNCTIONS
# =========================

def save_users():
    save_json(USERS_FILE, user_limits)

def save_pro():
    save_json(PRO_FILE, pro_users)

def save_refs():
    save_json(REF_FILE, referrals)

# =========================
# PRO CHECK
# =========================

def is_pro(user_id):

    user_id = str(user_id)

    if user_id not in pro_users:
        return False

    pro_data = pro_users[user_id]

    if pro_data == "forever":
        return True

    try:

        end_date = datetime.fromisoformat(pro_data)

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

    pro_data = pro_users[user_id]

    if pro_data == "forever":
        return "👑 Навсегда"

    try:

        end_date = datetime.fromisoformat(pro_data)

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

    # =========================
    # REFERRALS
    # =========================

    args = message.text.split()

    if len(args) > 1:

        ref_id = args[1]

        if ref_id != user_id:

            if user_id not in referrals:

                referrals[user_id] = ref_id

                if ref_id:

                    if ref_id in pro_users:

                        current_pro = pro_users[ref_id]

                        if current_pro != "forever":

                            try:

                                current_date = datetime.fromisoformat(current_pro)

                                if datetime.now() > current_date:
                                    current_date = datetime.now()

                            except:
                                current_date = datetime.now()

                            new_date = current_date + timedelta(days=7)

                            pro_users[ref_id] = new_date.isoformat()

                    else:

                        new_date = datetime.now() + timedelta(days=7)

                        pro_users[ref_id] = new_date.isoformat()

                    save_pro()

                save_refs()

                try:

                    await bot.send_message(
                        ref_id,
                        """
🎉 Ты пригласил друга!

💎 Бонус:
+7 ДНЕЙ PRO
"""
                    )

                except:
                    pass

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
💎 PRO 30 ДНЕЙ — $5

🆔 Твой ID:
{user_id}

Напиши админу:
@keks77777
"""
        )

    elif callback.data == "buy_forever":

        await callback.message.answer(
            f"""
👑 PRO НАВСЕГДА — $15

🆔 Твой ID:
{user_id}

Напиши админу:
@keks77777
"""
        )

    await callback.answer()

# =========================
# MAIN HANDLER
# =========================

@dp.message()
async def generate(message: Message):

    user_id = str(message.from_user.id)
    current_text = message.text

    if user_id not in user_limits:

        user_limits[user_id] = 0
        save_users()

    pro_status = is_pro(user_id)

    # =========================
    # REFERRALS
    # =========================

    if current_text == "👥 Рефералы":

        bot_info = await bot.get_me()

        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"

        await message.answer(
            f"""
👥 ТВОЯ РЕФЕРАЛЬНАЯ ССЫЛКА

🔗 {ref_link}

🎁 За каждого друга:
+7 ДНЕЙ PRO
"""
        )

        return

    # =========================
    # PRO
    # =========================

    if current_text == "💎 PRO":

        if pro_status:

            await message.answer(
                f"""
💎 У тебя уже есть PRO

{get_pro_status(user_id)}
"""
            )

        else:

            pro_menu = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="💎 PRO 30 ДНЕЙ — $5",
                            callback_data="buy_30"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="👑 PRO НАВСЕГДА — $15",
                            callback_data="buy_forever"
                        )
                    ]
                ]
            )

            await message.answer(
                """
💎 TikTok Viral AI PRO

• Без лимитов
• Быстрые ответы
• Premium Hooks
• Viral сценарии
• Лучшие идеи для TikTok
""",
                reply_markup=pro_menu
            )

        return

    # =========================
    # CUSTOM TOPIC
    # =========================

    if current_text == "✍️ Своя тема":

        waiting_custom_topic.add(user_id)

        await message.answer(
            "✍️ Напиши тему для TikTok"
        )

        return

    # =========================
    # LIMITS
    # =========================

    if not pro_status:

        if user_limits[user_id] >= FREE_LIMIT:

            await message.answer(
                """
❌ Бесплатные запросы закончились

💎 Купи PRO для безлимита
"""
            )

            return

    # =========================
    # SPAM PROTECTION
    # =========================

    if user_id in busy_users:

        await message.answer(
            "⏳ Подожди завершения прошлого запроса"
        )

        return

    busy_users[user_id] = True

    try:

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
Придумай 5 мощных TikTok hooks.
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

Формат:
🔥 HOOK
🎬 ИДЕЯ
📈 ХЕШТЕГИ
"""

        else:

            if user_id in busy_users:
                del busy_users[user_id]

            return

        loading = await message.answer(
            random.choice([
                "⏳ Генерирую контент...",
                "🔥 Анализирую TikTok...",
                "🚀 Создаю viral идею...",
                "📈 Подбираю hooks..."
            ])
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500
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

        final_text = f"""
━━━━━━━━━━━━━━━
🚀 TikTok Viral AI
━━━━━━━━━━━━━━━

{text}

━━━━━━━━━━━━━━━
📊 Осталось запросов:
{left_text}

💎 PRO = Безлимит
━━━━━━━━━━━━━━━
"""

        await loading.delete()

        await message.answer(
            final_text[:4000]
        )

    except Exception as e:

        await message.answer(
            f"❌ Ошибка:\n{e}"
        )

    finally:

        if user_id in busy_users:
            del busy_users[user_id]

# =========================
# MAIN
# =========================

async def main():

    print("Бот запущен 🚀")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```
