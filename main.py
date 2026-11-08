import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

TELEGRAM_BOT_TOKEN = "9096171142:AAEuOhMiWZvKwJgh7MznzxjiNVUBY5l2pIw"
CRYPTO_PAY_TOKEN = "671278:AAUtZLG9F0jDQSYp80SbwRfHV5KTccpocew"
WEB_APP_URL = "https://autoinspectpro.github.io"  # Замени на свою точную ссылку, если в конце есть имя репозитория

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

users_balance = {}
user_assets = {}

assets_prices = {
    "Криптомем": 100,
    "Токен Хайпа": 150,
    "Цифровое золото": 500,
    "Энергия Сообщества": 50
}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_balance:
        users_balance[user_id] = 0
        user_assets[user_id] = {k: 0 for k in assets_prices}
        
    # Создаем красивую кнопку для открытия Mini App
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть Биржу Mini App", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])
    
    text = (
        "🚀 **Добро пожаловать в биржевой симулятор!**\n\n"
        "Теперь у нас есть современный интерфейс. Нажми кнопку ниже, чтобы открыть Mini App 👇"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

@dp.message(Command("deposit"))
async def cmd_deposit(message: types.Message):
    async with aiohttp.ClientSession() as session:
        url = "https://pay.crypt.bot/api/createInvoice"
        headers = {"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN}
        payload = {
            "asset": "USDT",
            "amount": "1.0",
            "description": "Покупка 1000 кредитов в биржевом симуляторе",
            "payload": f"user_id_{message.from_user.id}"
        }
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            if data.get("ok"):
                invoice_url = data["result"]["pay_url"]
                await message.answer(
                    f"🔗 **Счет создан!**\n\nНажми на ссылку ниже для оплаты 1 USDT через CryptoBot:\n{invoice_url}",
                    parse_mode="Markdown"
                )
            else:
                await message.answer("Ошибка при создании счета. Попробуй позже.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
