import os
import json
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command

load_dotenv()

router = Router()

# Тарифы с ценами в рублях
TARIFFS = {
    "1 месяц": {"months": 1, "price": 100, "description": "Размещение на 1 месяц"},
    "3 месяца": {"months": 3, "price": 250, "description": "Размещение на 3 месяца"},
    "6 месяцев": {"months": 6, "price": 450, "description": "Размещение на 6 месяцев"},
    "1 год": {"months": 12, "price": 800, "description": "Размещение на 1 год"}
}


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


@router.message()
async def handle_all_messages(message: types.Message):
    # Обрабатываем данные из мини-приложения
    if message.web_app_data:
        await handle_web_app_data(message)
    else:
        # Игнорируем обычные сообщения
        pass


async def handle_web_app_data(message: types.Message):
    try:
        print("Получены данные из мини-приложения:", message.web_app_data.data)

        data = json.loads(message.web_app_data.data)
        plan_name = data.get('plan')
        user_id = data.get('user_id')

        print(f"План: {plan_name}, User ID: {user_id}")

        if plan_name not in TARIFFS:
            await message.answer("❌ Ошибка: тариф не найден")
            return

        tariff = TARIFFS[plan_name]

        # Создаем кнопку оплаты через ЮКассу
        prices = [types.LabeledPrice(label=plan_name, amount=tariff["price"] * 100)]  # в копейках

        await message.answer_invoice(
            title=f"Реклама в паблике - {plan_name}",
            description=tariff["description"],
            provider_token="381764678:TEST:87885",  # Токен тестового режима ЮКассы
            currency="RUB",
            prices=prices,
            payload=json.dumps({
                "plan": plan_name,
                "months": tariff["months"],
                "user_id": user_id
            }),
            start_parameter="create_invoice"
        )

    except json.JSONDecodeError as e:
        print(f"Ошибка JSON: {e}")
        await message.answer("❌ Ошибка формата данных")
    except Exception as e:
        print(f"Общая ошибка: {e}")
        await message.answer("❌ Произошла ошибка при обработке заказа")


# Обработка предварительного запроса оплаты
@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


# Обработка успешной оплаты
@router.message(lambda message: message.successful_payment is not None)
async def process_successful_payment(message: types.Message):
    try:
        payload = json.loads(message.successful_payment.invoice_payload)
        plan_name = payload.get('plan')
        months = payload.get('months')
        user_id = payload.get('user_id')

        # Сообщение об успешной оплате
        success_text = (
            f"✅ **Спасибо за заказ!**\n\n"
            f"**Тариф:** {plan_name}\n"
            f"**Срок:** {months} месяцев\n"
            f"**Сумма:** {message.successful_payment.total_amount // 100} руб.\n\n"
            f"С вами свяжутся для уточнения деталей размещения.\n"
            f"ID заказа: {user_id}"
        )

        await message.answer(success_text, parse_mode="Markdown")

    except Exception as e:
        print(f"Ошибка обработки оплаты: {e}")
        await message.answer("✅ Оплата прошла успешно! Спасибо за заказ.")


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)

    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())