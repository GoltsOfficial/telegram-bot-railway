import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command

load_dotenv()

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    web_app_url = "https://goltsofficial.github.io/telegram_seller_assistant/"
    web_app = types.WebAppInfo(url=web_app_url)

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="✨ Заказать рекламу", web_app=web_app)]],
        resize_keyboard=True
    )

    await message.answer("Добро пожаловать! Нажмите кнопку для заказа рекламы.", reply_markup=keyboard)


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("/start - начать\n/help - помощь")


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())