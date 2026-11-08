import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

TELEGRAM_BOT_TOKEN = "9096171142:AAEuOhMiWZvKwJgh7MznzxjiNVUBY5l2pIw"
CRYPTO_PAY_TOKEN = "671278:AAUtZLG9F0jDQSYp80SbwRfHV5KTccpocew"

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
        
    text = (
        "🚀 **Добро пожаловать в биржевой симулятор!**\n\n"
        "Покупай виртуальные активы, следи за курсом и соревнуйся за лидерство.\n\n"
        "💳 /balance — Проверить баланс и портфель\n"
        "💎 /deposit — Пополнить баланс за криптовалюту\n"
        "📈 /market — Рынок активов\n"
        "🛒 /buy <Название> <Кол-во> — Купить актив"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("balance"))
async def cmd_balance(message: types.Message):
    user_id = message.from_user.id
    balance = users_balance.get(user_id, 0)
    assets = user_assets.get(user_id, {})
    
    portfolio_text = "\n".join([f"• {name}: {count}" for name, count in assets.items()])
    if not any(assets.values()):
        portfolio_text = "Пусто"
    
    text = (
        f"💰 **Твой баланс:** {balance} кредитов\n\n"
        f"📦 **Твой портфель активов:**\n{portfolio_text}"
    )
    await message.answer(text, parse_mode="Markdown")

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

@dp.message(Command("market"))
async def cmd_market(message: types.Message):
    market_text = (
        "📈 **Текущие цены на бирже:**\n\n"
        "• 🐶 Криптомем — 100 кредитов\n"
        "• ⚡️ Токен Хайпа — 150 кредитов\n"
        "• 🪙 Цифровое золото — 500 кредитов\n"
        "• 🔮 Энергия Сообщества — 50 кредитов\n\n"
        "Используй /buy <Название> <Кол-во> для покупки."
    )
    await message.answer(market_text, parse_mode="Markdown")

@dp.message(Command("buy"))
async def cmd_buy(message: types.Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Используй формат: /buy <Название актива> <Количество>")
        return

    asset_name = args[1].capitalize()
    try:
        quantity = int(args[2])
    except ValueError:
        await message.answer("Укажи корректное целое число для покупки.")
        return

    if asset_name not in assets_prices:
        await message.answer("Такого актива нет на рынке.")
        return

    total_cost = assets_prices[asset_name] * quantity
    user_id = message.from_user.id

    if users_balance.get(user_id, 0) < total_cost:
        await message.answer("Недостаточно кредитов для покупки.")
        return

    users_balance[user_id] -= total_cost
    user_assets[user_id][asset_name] = user_assets[user_id].get(asset_name, 0) + quantity

    await message.answer(f"✅ Успешно куплено: {quantity} шт. {asset_name}!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
