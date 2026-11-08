import os
import asyncio
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

TELEGRAM_BOT_TOKEN = "9096171142:AAEuOhMiWZvKwJgh7MznzxjiNVUBY5l2pIw"
CRYPTO_PAY_TOKEN = "671278:AAUtZLG9F0jDQSYp80SbwRfHV5KTccpocew"
WEB_APP_URL = "https://autoinspectpro.github.io/CryptoTrade/"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

users_balance = {}
user_assets = {}

assets_prices = {
    "CyberCoin": 200,
    "Etherium Pro": 500,
    "Solaris": 100,
    "MemeDoge": 50
}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_balance:
        users_balance[user_id] = 1000.0
        user_assets[user_id] = {k: 0 for k in assets_prices}
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть Биржу Mini App", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])
    
    text = (
        "🚀 **Добро пожаловать в биржевой симулятор!**\n\n"
        "Нажми кнопку ниже, чтобы открыть Mini App и начать торговлю."
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

@dp.message(Command("deposit"))
async def cmd_deposit(message: types.Message):
    # Запасной вариант через команду в боте
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
                    parse_Mode="Markdown"
                )
            else:
                await message.answer("Ошибка при создании счета. Попробуй позже.")

# API эндпоинт для связи с Mini App
async def api_deposit(request):
    try:
        data = await request.json()
        user_id = data.get("user_id", 0)
        
        async with aiohttp.ClientSession() as session:
            url = "https://pay.crypt.bot/api/createInvoice"
            headers = {"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN}
            payload = {
                "asset": "USDT",
                "amount": "1.0",
                "description": "Покупка кредитов в биржевом симуляторе",
                "payload": f"user_id_{user_id}"
            }
            async with session.post(url, json=payload, headers=headers) as resp:
                res_data = await resp.json()
                if res_data.get("ok"):
                    pay_url = res_data["result"]["pay_url"]
                    return web.json_response({"pay_url": pay_url})
                else:
                    return web.json_response({"pay_url": None}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.add_routes([
        web.get("/", handle),
        web.post("/deposit-api", api_deposit)
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
