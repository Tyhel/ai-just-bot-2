import asyncio
import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, BufferedInputFile
from aiogram.exceptions import TelegramBadRequest
from fastapi import FastAPI, Request, Response
import uvicorn
import logging

# === ТОКЕНЫ ===
BOT_TOKEN = "8328706906:AAEcSN2x88oLLsKzzV1lIEfJ6zvjIweK6uk"
MERCHANT_TOKEN = "516202:AA7y0K7T2YhC94z0lLMOmWPeKAVs9mGEu62"

# === ЗАГРУЗКА ПРОМТОВ (если файлы есть в репозитории) ===
def load_prompts(filepath, count):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        prompts = []
        for line in lines:
            clean = line.split('. "', 1)[-1].rstrip('"\n')
            if not clean and '"' in line:
                clean = line.split('. "', 1)[-1].rstrip('"').rstrip('\n')
            prompts.append(clean)
        return "\n\n".join([f"🔹 Промт {i+1}:\n{p}" for i, p in enumerate(prompts[:count])])
    except Exception as e:
        print(f"⚠️ Ошибка загрузки {filepath}: {e}")
        return "Промты временно недоступны."

PROMPTS_50 = load_prompts("Qwen__20260115_smsdj5bpi.txt", 50)
PROMPTS_25 = load_prompts("Топовые 25 Промптов для NanoBanana, Midjourney, SDXL, DALL·E 3.txt", 25)

# === ИНИЦИАЛИЗАЦИЯ ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# === КЛАВИАТУРЫ ===
def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="🛍️ Товары", callback_data="products")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
    ])

def back_to_menu_button():
    return [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")]

def back_to_products_button():
    return [InlineKeyboardButton(text="⬅️ Назад к товарам", callback_data="products")]

# === /start ===
@dp.message(Command("start"))
async def start_handler(message: Message):
    text = (
        f"🌌 <b>Добро пожаловать в Ai.Just</b>\n\n"
        f"Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Вы подключились к источнику премиум-промтов для генерации будущего.\n\n"
        "▫️ 50 футуристических сцен\n"
        "▫️ 25 эмоциональных историй\n"
        "▫️ Полная совместимость с NanoBanana, Midjourney, SDXL\n\n"
        "─── ⋆⋅☆⋅⋆ ───\n"
        "Выберите раздел ниже:"
    )
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="HTML")

# === МЕНЮ ===
@dp.callback_query(lambda c: c.data == "balance")
async def balance_handler(callback: CallbackQuery):
    text = (
        "💰 <b>Ваш баланс:</b>\n\n"
        "На данный момент баланс не используется — все покупки совершаются напрямую через криптовалюту.\n\n"
        "Вы можете купить товар за 0.1 USDT в любое время."
    )
    try:
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[back_to_menu_button()]),
            parse_mode="HTML"
        )
    except TelegramBadRequest:
        pass
    await callback.answer()

@dp.callback_query(lambda c: c.data == "products")
async def products_handler(callback: CallbackQuery):
    text = "🛍️ <b>Выберите товар:</b>"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 50 футуристических промтов", callback_data="buy_50pack")],
        [InlineKeyboardButton(text="🔥 Топ-25 промтов (NanoBanana, MJ, SDXL)", callback_data="buy_25pack")],
        back_to_menu_button()
    ])
    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except TelegramBadRequest:
        pass
    await callback.answer()

@dp.callback_query(lambda c: c.data == "help")
async def help_handler(callback: CallbackQuery):
    text = (
        "❓ <b>Помощь</b>\n\n"
        "1️⃣ Перейдите в «Товары»\n"
        "2️⃣ Выберите нужный набор промтов\n"
        "3️⃣ Нажмите «Купить за 0.1 USDT»\n"
        "4️⃣ Оплатите через Crypto Bot\n"
        "5️⃣ Получите промты автоматически\n\n"
        "💡 Все промты готовы к использованию в Midjourney, DALL·E 3, Stable Diffusion, NanoBanana."
    )
    try:
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[back_to_menu_button()]),
            parse_mode="HTML"
        )
    except TelegramBadRequest:
        pass
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    text = "🌌 Вы в главном меню.\n\nВыберите раздел:"
    try:
        await callback.message.edit_text(text, reply_markup=get_main_menu())
    except TelegramBadRequest:
        pass
    await callback.answer()

# === ВЫБОР И ПОКУПКА ТОВАРА ===
@dp.callback_query(lambda c: c.data in ["buy_50pack", "buy_25pack"])
async def select_product(callback: CallbackQuery):
    product_id = callback.data
    if product_id == "buy_50pack":
        desc = "Полный набор из 50 футуристических промтов для генерации изображений, видео, UI и музыки."
    else:
        desc = "Топ-25 промтов для NanoBanana, Midjourney, SDXL и DALL·E 3. Романтика, приключения, повседневность — с персонализацией лиц."

    text = (
        f"<b>🛒 Вы выбрали:</b>\n\n{desc}\n\n"
        "💰 Цена: <b>0.1 USDT</b>\n"
        "⚡ После оплаты — бот автоматически пришлёт пакет промтов 🖼️"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Купить за 0.1 USDT", callback_data=f"confirm_{product_id}")],
        back_to_products_button()
    ])
    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except TelegramBadRequest:
        pass
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("confirm_"))
async def confirm_purchase(callback: CallbackQuery):
    product_id = callback.data.replace("confirm_", "")
    user_id = callback.from_user.id
    payload = f"{product_id}_user_{user_id}"

    try:
        response = requests.post(
            "https://pay.crypt.bot/api/createInvoice",
            headers={"Crypto-Pay-API-Token": MERCHANT_TOKEN},
            json={
                "asset": "USDT",
                "amount": "0.1",
                "description": "Премиум-промты для AI-генераторов",
                "payload": payload
            }
        )
        data = response.json()
        if data.get("ok"):
            pay_url = data["result"]["pay_url"]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➡️ Оплатить 0.1 USDT", url=pay_url)],
                back_to_products_button()
            ])
            try:
                await callback.message.edit_text(
                    "✅ Счёт создан!\n\nНажмите кнопку ниже, чтобы завершить покупку:",
                    reply_markup=keyboard
                )
            except TelegramBadRequest:
                pass
        else:
            error_msg = data.get("error", {}).get("message", "Неизвестная ошибка")
            await callback.message.answer(f"❌ Ошибка: {error_msg}")
    except Exception as e:
        logging.error(f"Ошибка при создании счёта: {e}")
        await callback.message.answer("⚠️ Техническая ошибка.")
    await callback.answer()

# === WEBHOOK с отправкой ФАЙЛОМ ===
@app.post("/crypto-webhook")
async def crypto_webhook(request: Request):
    print("📥 [WEBHOOK] Запрос получен!")
    try:
        data = await request.json()
        print(f"📄 [WEBHOOK] Внешний JSON: {data}")
    except Exception as e:
        print(f"❌ [WEBHOOK] Ошибка парсинга: {e}")
        return Response(status_code=200)

    inner_payload = data.get("payload", {})
    if not isinstance(inner_payload, dict):
        print("⚠️ [WEBHOOK] Неверный формат payload")
        return Response(status_code=200)

    status = inner_payload.get("status")
    print(f"🔍 [WEBHOOK] Статус: '{status}'")

    if status != "paid":
        print("ℹ️ [WEBHOOK] Статус не 'paid'")
        return Response(status_code=200)

    payload_str = inner_payload.get("payload", "")
    print(f"📦 [WEBHOOK] Payload: '{payload_str}'")

    user_id = None
    file_content = ""
    filename = ""

    if payload_str.startswith("buy_50pack_user_"):
        try:
            user_id = int(payload_str.replace("buy_50pack_user_", ""))
            file_content = PROMPTS_50
            filename = "50_futuristic_prompts.txt"
        except ValueError:
            print("❌ [WEBHOOK] Ошибка извлечения user_id из buy_50pack")
    elif payload_str.startswith("buy_25pack_user_"):
        try:
            user_id = int(payload_str.replace("buy_25pack_user_", ""))
            file_content = PROMPTS_25
            filename = "top_25_prompts.txt"
        except ValueError:
            print("❌ [WEBHOOK] Ошибка извлечения user_id из buy_25pack")
    else:
        print("⚠️ [WEBHOOK] Неизвестный payload")
        return Response(status_code=200)

    if user_id and file_content:
        try:
            print(f"📤 [WEBHOOK] Отправка файла '{filename}' пользователю {user_id}")
            # ✅ Отправка как файл
            document = BufferedInputFile(
                file_content.encode("utf-8"),
                filename=filename
            )
            await bot.send_document(
                chat_id=user_id,
                document=document,
                caption=f"🎉 Спасибо за покупку!\n\nВаш файл: <b>{filename}</b>",
                parse_mode="HTML"
            )
            print(f"✅ [WEBHOOK] Файл выдан пользователю {user_id}")
        except Exception as e:
            print(f"❌ [WEBHOOK] Ошибка отправки: {e}")
    else:
        print("❌ [WEBHOOK] Нет данных для отправки")

    return Response(status_code=200)

# === ЗАПУСК (без потоков!) ===
async def main():
    polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    print("✅ Бот и webhook запущены!")
    asyncio.run(main())