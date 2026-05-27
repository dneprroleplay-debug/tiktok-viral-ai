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
from openai import OpenAI
import asyncio
import json
import os
from datetime import datetime, timedelta

BOT_TOKEN = "8854279157:AAGny_hfazw7DXKn9jo8-oARpIng6uXSuhc"

ADMIN_ID = 805924502

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

FREE_LIMIT = 50

USERS_FILE = "users.json"
PRO_FILE = "pro_users.json"
REF_FILE = "refs.json"

busy_users = {}
waiting_custom_topic = set()

# =========================
# ЗАГРУЗКА БАЗ
# =========================

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r", encoding="utf-8") as file:
        user_limits = json.load(file)
else:
    user_limits = {}

if os.path.exists(PRO_FILE):
    with open(PRO_FILE, "r", encoding="utf-8") as file:
        pro_users = json.load(file)
else:
    pro_users = {}

if os.path.exists(REF_FILE):
    with open(REF_FILE, "r", encoding="utf-8") as file:
        referrals = json.load(file)
else:
    referrals = {}

# =========================
# СОХРАНЕНИЕ
# =========================

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(user_limits, file, ensure_ascii=False, indent=4)

def save_pro():
    with open(PRO_FILE, "w", encoding="utf-8") as file:
        json.dump(pro_users, file, ensure_ascii=False, indent=4)

def save_refs():
    with open(REF_FILE, "w", encoding="utf-8") as file:
        json.dump(referrals, file, ensure_ascii=False, indent=4)

# =========================
# ПРОВЕРКА PRO
# =========================

def is_pro(user_id):

    user_id = str(user_id)

    if user_id not in pro_users:
        return False

    pro_data = pro_users[user_id]

    # НАВСЕГДА
    if pro_data == "forever":
        return True

    # ДАТА
    end_date = datetime.fromisoformat(pro_data)

    if datetime.now() < end_date:
        return True

    # УДАЛЯЕМ ПРОСРОЧКУ
    del pro_users[user_id]
    save_pro()

    return False

# =========================
# СТАТУС PRO
# =========================

def get_pro_status(user_id):

    user_id = str(user_id)

    if user_id not in pro_users:
        return "❌ Нет"

    pro_data = pro_users[user_id]

    if pro_data == "forever":
        return "👑 Навсегда"

    end_date = datetime.fromisoformat(pro_data)

    return f"💎 До {end_date.strftime('%d.%m.%Y')}"

# =========================
# МЕНЮ
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

    # Новый пользователь
    if user_id not in user_limits:
        user_limits[user_id] = 0
        save_users()

    # =========================
    # РЕФЕРАЛКА
    # =========================

    args = message.text.split()

    if len(args) > 1:

        ref_id = args[1]

        # Нельзя пригласить себя
        if ref_id != user_id:

            # Если пользователя еще не приглашали
            if user_id not in referrals:

                referrals[user_id] = ref_id

                # БОНУС PRO НА 7 ДНЕЙ
                if ref_id:

                    # Если уже есть PRO
                    if ref_id in pro_users:

                        current_pro = pro_users[ref_id]

                        # Если forever
                        if current_pro == "forever":
                            pass

                        else:

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
# INLINE КНОПКИ
# =========================

@dp.callback_query()
async def callbacks(callback: CallbackQuery):

    user_id = str(callback.from_user.id)

    # 30 ДНЕЙ
    if callback.data == "buy_30":

        await callback.message.answer(
            f"""
💎 PRO 30 ДНЕЙ — $4.99

💳 Оплата скоро будет подключена.

🆔 Твой ID:
{user_id}

Отправь скрин оплаты админу:
@keks77777
"""
        )

    # НАВСЕГДА
    elif callback.data == "buy_forever":

        await callback.message.answer(
            f"""
👑 PRO НАВСЕГДА — $14.99

💳 Оплата скоро будет подключена.

🆔 Твой ID:
{user_id}

Отправь скрин оплаты админу:
@keks77777
"""
        )

    await callback.answer()

# =========================
# ВСЕ СООБЩЕНИЯ
# =========================

@dp.message()
async def generate(message: Message):

    user_id = str(message.from_user.id)
    current_text = message.text

    # =========================
    # АДМИН КОМАНДЫ
    # =========================

    if message.from_user.id == ADMIN_ID:

        # СТАТИСТИКА
        if current_text == "/stats":

            total_users = len(user_limits)
            total_pro = len(pro_users)
            total_refs = len(referrals)

            await message.answer(
                f"""
📊 СТАТИСТИКА БОТА

👥 Пользователей:
{total_users}

💎 PRO пользователей:
{total_pro}

🔗 Рефералов:
{total_refs}

🔥 Бесплатный лимит:
{FREE_LIMIT}

🚀 Бот работает отлично
"""
            )

            return

        # ВЫДАТЬ PRO
        if current_text.startswith("/givepro"):

            try:
                parts = current_text.split()

                target_id = parts[1]
                days = int(parts[2])

                end_date = datetime.now() + timedelta(days=days)

                pro_users[target_id] = end_date.isoformat()

                save_pro()

                await message.answer(
                    f"""
✅ PRO активирован

🆔 ID: {target_id}
📅 Дней: {days}
"""
                )

            except:

                await message.answer(
                    "❌ Используй:\n/givepro ID ДНИ"
                )

            return

        # FOREVER
        if current_text.startswith("/giveforever"):

            try:
                target_id = current_text.split()[1]

                pro_users[target_id] = "forever"

                save_pro()

                await message.answer(
                    f"""
👑 FOREVER PRO активирован

🆔 ID: {target_id}
"""
                )

            except:

                await message.answer(
                    "❌ Используй:\n/giveforever ID"
                )

            return

        # УДАЛИТЬ PRO
        if current_text.startswith("/removepro"):

            try:
                target_id = current_text.split()[1]

                if target_id in pro_users:

                    del pro_users[target_id]

                    save_pro()

                    await message.answer(
                        f"""
❌ PRO удален

🆔 ID: {target_id}
"""
                    )

                else:

                    await message.answer(
                        "❌ У пользователя нет PRO"
                    )

            except:

                await message.answer(
                    "❌ Используй:\n/removepro ID"
                )

            return

    # =========================
    # РЕФЕРАЛЫ
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
    # НОВЫЙ ЮЗЕР
    # =========================

    if user_id not in user_limits:
        user_limits[user_id] = 0
        save_users()

    pro_status = is_pro(user_id)

    # =========================
    # PRO КНОПКА
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
                            text="💎 PRO 30 ДНЕЙ — $4.99",
                            callback_data="buy_30"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="👑 PRO НАВСЕГДА — $14.99",
                            callback_data="buy_forever"
                        )
                    ]
                ]
            )

            await message.answer(
                """
💎 TikTok Viral AI PRO

🔥 Возможности:

• Безлимитные запросы
• Premium hooks
• Лучшие TikTok идеи
• Быстрые ответы
• Viral сценарии

💰 Выбери подписку:
""",
                reply_markup=pro_menu
            )

        return

    # =========================
    # СВОЯ ТЕМА
    # =========================

    if current_text == "✍️ Своя тема":

        waiting_custom_topic.add(user_id)

        await message.answer(
            "✍️ Напиши тему для TikTok"
        )

        return

    # =========================
    # ЛИМИТ
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
    # СПАМ ЗАЩИТА
    # =========================

    if user_id in busy_users:

        if busy_users[user_id] == current_text:

            await message.answer(
                "⏳ Ты уже сделал этот запрос, нужно подождать"
            )

        else:

            await message.answer(
                "⏳ Подожди пока закончится прошлый запрос"
            )

        return

    busy_users[user_id] = current_text

    try:

        # ИДЕЯ РОЛИКА
        if current_text == "🎬 Идея ролика":

            prompt = """
            Придумай 3 вирусные идеи для TikTok.

            Формат:
            🔥 HOOK
            🎬 ИДЕЯ
            📈 ХЕШТЕГИ
            """

        # HOOK
        elif current_text == "🔥 Hook":

            prompt = """
            Придумай 5 мощных TikTok hooks
            для удержания внимания.
            """

        # ХЕШТЕГИ
        elif current_text == "📈 Хештеги":

            prompt = """
            Придумай вирусные TikTok хештеги.
            """

        # СВОЯ ТЕМА
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

        # ЗАГРУЗКА
        loading_texts = [
            "⏳ Генерирую вирусный контент...",
            "🔥 Анализирую TikTok тренды...",
            "🚀 Создаю viral сценарий...",
            "📈 Подбираю лучшие hooks..."
        ]

        import random

        wait_message = await message.answer(
            random.choice(loading_texts)
        )

        # AI
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

        # ЛИМИТЫ
        if not pro_status:

            user_limits[user_id] += 1
            save_users()

        left_requests = FREE_LIMIT - user_limits[user_id]

        if pro_status:
            left_text = "♾ Безлимит"
        else:
            left_text = str(left_requests)

        # КРАСИВЫЙ ОТВЕТ
        beautiful_text = f"""
━━━━━━━━━━━━━━━
🚀 TikTok Viral AI 🚀
━━━━━━━━━━━━━━━

{text}

━━━━━━━━━━━━━━━
📊 Осталось запросов:
{left_text}

💎 PRO = Безлимит
━━━━━━━━━━━━━━━
"""

        await wait_message.delete()

        await message.answer(
            beautiful_text[:4000]
        )

    except Exception as e:

        await message.answer(
            f"❌ Ошибка:\n{e}"
        )

    finally:

        if user_id in busy_users:
            del busy_users[user_id]

# =========================
# ЗАПУСК
# =========================

async def main():

    print("Бот запущен 🚀")

    await dp.start_polling(bot)

asyncio.run(main())