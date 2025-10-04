import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

# ===================== Загрузка токена =====================
load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN not found in .env file")

# ===================== Логирование =====================
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ===================== Состояния =====================
class AdForm(StatesGroup):
    title = State()
    photos = State()
    address = State()
    description = State()
    rent_or_own = State()
    revenue = State()
    profit = State()
    staff_count = State()
    finance_file = State()
    price = State()
    category = State()
    contact = State()

# ===================== Категории =====================
categories = {
    "Услуги": "🛠",
    "ПунктыВыдачи": "📦",
    "Бьюти": "💄",
    "ГАБ": "🏢",
    "Производство": "🏭",
    "Общепит": "🍽",
    "ТоварныйБизнес": "📦",
    "Автобизнес": "🚗"
}

# ===================== Градации стоимости =====================
price_tags = [
    ("до500т", 0, 500_000),
    ("до1млн", 500_001, 1_000_000),
    ("до1.5млн", 1_000_001, 1_500_000),
    ("до2млн", 1_500_001, 2_000_000),
    ("до3млн", 2_000_001, 3_000_000),
    ("до5млн", 3_000_001, 5_000_000),
]

# ===================== Старт =====================
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("/new"))
    await message.answer(
        "Привет! 👋\n\n"
        "Этот бот поможет вам создать объявление для продажи вашего бизнеса.\n"
        "Вы будете отвечать на пошаговые вопросы, и в итоге объявление будет опубликовано в нашем канале.\n\n"
        "Нажмите /new, чтобы начать.",
        reply_markup=kb
    )

# ===================== 1. Название =====================
@dp.message_handler(commands=['new'])
async def process_title(message: types.Message):
    await AdForm.title.set()
    await message.answer("🏷️ Введите название бизнеса:\n<i>Краткое и понятное название, без лишних слов</i>")

@dp.message_handler(state=AdForm.title)
async def title_entered(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await AdForm.photos.set()
    await message.answer("📸 Пришлите фото бизнеса. Можно несколько. После загрузки всех фото напишите 'Готово'.")

# ===================== 2. Фото =====================
@dp.message_handler(lambda message: message.text and message.text.lower() == "готово", state=AdForm.photos)
async def photos_done(message: types.Message, state: FSMContext):
    await AdForm.address.set()
    await message.answer("📍 Введите адрес:\n<i>Указывайте точный адрес с городом и улицей</i>")

@dp.message_handler(content_types=types.ContentType.PHOTO, state=AdForm.photos)
async def photo_received(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer("Фото сохранено. Пришлите ещё или напишите 'Готово'.")

# ===================== 3. Адрес =====================
@dp.message_handler(state=AdForm.address)
async def address_entered(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await AdForm.description.set()
    await message.answer("📝 Введите описание бизнеса:\n<i>Кратко о возрасте бизнеса, росте, сотрудниках, особенностях</i>")

# ===================== 4. Описание =====================
@dp.message_handler(state=AdForm.description)
async def description_entered(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await AdForm.rent_or_own.set()
    await message.answer("🏠 Аренда или собственность?\n<i>Укажите стоимость аренды или 'собственность'</i>")

# ===================== 5. Аренда/собственность =====================
@dp.message_handler(state=AdForm.rent_or_own)
async def rent_entered(message: types.Message, state: FSMContext):
    await state.update_data(rent_or_own=message.text)
    await AdForm.revenue.set()
    await message.answer("💰 Укажите месячную выручку:\n<i>Укажите средние показатели за последний месяц</i>")

# ===================== 6. Выручка =====================
@dp.message_handler(state=AdForm.revenue)
async def revenue_entered(message: types.Message, state: FSMContext):
    await state.update_data(revenue=message.text)
    await AdForm.profit.set()
    await message.answer("📈 Укажите чистую прибыль:\n<i>Укажите средние показатели за последний месяц</i>")

# ===================== 7. Чистая прибыль =====================
@dp.message_handler(state=AdForm.profit)
async def profit_entered(message: types.Message, state: FSMContext):
    await state.update_data(profit=message.text)
    await AdForm.staff_count.set()
    await message.answer("👥 Укажите количество сотрудников:\n<i>Укажите количество людей в штате</i>")

# ===================== 8. Кол-во сотрудников =====================
@dp.message_handler(state=AdForm.staff_count)
async def staff_entered(message: types.Message, state: FSMContext):
    await state.update_data(staff_count=message.text)
    await AdForm.finance_file.set()
    await message.answer(
        "📊 Прикрепите финансовую модель (.xlsx) или напишите 'Пропустить'.\n"
        "<i>Не является коммерческой тайной</i>\n"
        "Пример шаблона: https://docs.google.com/spreadsheets/d/1Vcn68ThO7yEWCQdLTZAsWVQc5c-V19B0wNLo0zIx_og/edit?usp=sharing"
    )

# ===================== 9. Финансовая модель =====================
@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=AdForm.finance_file)
async def finance_received(message: types.Message, state: FSMContext):
    await state.update_data(finance_file=message.document.file_id)
    await AdForm.price.set()
    await message.answer("💵 Укажите стоимость бизнеса:\n<i>Укажите адекватную цену</i>")

@dp.message_handler(lambda message: message.text.lower() == "пропустить", state=AdForm.finance_file)
async def finance_skipped(message: types.Message, state: FSMContext):
    await state.update_data(finance_file=None)
    await AdForm.price.set()
    await message.answer("💵 Укажите стоимость бизнеса:\n<i>Укажите адекватную цену</i>")

# ===================== 10. Стоимость =====================
@dp.message_handler(state=AdForm.price)
async def price_entered(message: types.Message, state: FSMContext):
    price_text = message.text.replace(" ", "").replace("т", "000")
    price_number = int(''.join(filter(str.isdigit, price_text)))
    tag = None
    for t, low, high in price_tags:
        if low <= price_number <= high:
            tag = t
            break
    await state.update_data(price=message.text, price_tag=tag)
    await AdForm.category.set()
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for c in categories.keys():
        kb.add(c)
    await message.answer("🏷️ Выберите категорию бизнеса:", reply_markup=kb)

# ===================== 11. Категория =====================
@dp.message_handler(state=AdForm.category)
async def category_entered(message: types.Message, state: FSMContext):
    category = message.text.replace(" ", "")
    if category not in categories:
        await message.answer("Выберите категорию из предложенных кнопок.")
        return
    await state.update_data(category=category)
    await AdForm.contact.set()
    await message.answer("📞 Укажите контакт для связи с продавцом:\n<i>Телефон, Telegram или email</i>")

# ===================== 12. Контакт =====================
@dp.message_handler(state=AdForm.contact)
async def contact_entered(message: types.Message, state: FSMContext):
    contact = message.text.strip()  # Убираем пробелы в начале и конце
    if not contact:
        await message.answer("Контакт не может быть пустым. Укажите телефон, Telegram или email.")
        return

    await state.update_data(contact=contact)
    data = await state.get_data()

    # Формируем текст объявления
    text = f"🏷️ <b>{data['title']}</b>\n" \
           f"📍 Адрес: {data['address']}\n" \
           f"📝 Описание: {data['description']}\n" \
           f"🏠 Аренда/собственность: {data['rent_or_own']}\n" \
           f"💰 Выручка: {data['revenue']}\n" \
           f"📈 Чистая прибыль: {data['profit']}\n" \
           f"👥 Сотрудники: {data['staff_count']}\n" \
           f"📊 Финансовая модель: {'прикреплено' if data.get('finance_file') else 'не прикреплено'}\n" \
           f"💵 Стоимость: {data['price']}\n" \
           f"📞 Контакт: {contact}\n\n" \
           f"#{data['category']} #{data.get('price_tag', '')}"

    # ===================== Отправка объявления в канал =====================
    CHANNEL_ID = -1002077624751  # ID твоего канала

    try:
        # Если есть фото
        if data.get("photos"):
            media = [
                InputMediaPhoto(
                    media=p,
                    caption=text if i == 0 else ""
                ) for i, p in enumerate(data["photos"])
            ]
            await bot.send_media_group(chat_id=CHANNEL_ID, media=media)
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=text)

        # Если есть файл — отправляем его отдельным сообщением
        if data.get("finance_file"):
            await bot.send_document(
                chat_id=CHANNEL_ID,
                document=data["finance_file"],
                caption="📊 Финансовая модель"
            )

    except Exception as e:
        await message.answer(f"Ошибка при отправке объявления: {e}")
        await state.finish()
        return

    await message.answer("✅ Ваше объявление отправлено!")
    await state.finish()

# ===================== Запуск =====================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)