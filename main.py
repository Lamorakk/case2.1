import logging
import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder

API_TOKEN = "7333238266:AAEz4RVqD3JKgdlpAzCpapXqwOdsECjz-I0"
ADMIN_CHAT_ID = '-1002181544885'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

class Survey(StatesGroup):
    start = State()
    age = State()
    city = State()
    schedule = State()
    name = State()
    contact_info = State()

@router.message(CommandStart())
async def send_welcome(message: types.Message, state: FSMContext):
    user_data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username
    }
    await state.update_data(**user_data)
    await message.answer(
        "Вас вітає «Luxury studio»\n"
        "Ми є одними з лідерів ринку в цій ніші, тому шукаємо активних та амбітних людей в наші ряди😉\n")
    await message.answer(
        "Я Єва, бот-помічник модельної агенції «Luxury studio». Я допоможу тобі оформити анкету на професію веб-модель.\n\n"
        "Професія, де абсолютно кожна дівчина зможе здійснити свою мрію і вийти на дохід від 1500$ навіть без досвіду.\n"
        "Та від 3000$ для дівчат з досвідом. Давай познайомимось ближче.\n\n"
        "Дай відповідь на 5 питань (це займе 2 хвилини твого часу), і ми продовжимо спілкування далі. Ти згодна?\n",
        reply_markup=ReplyKeyboardBuilder().button(text="Так").as_markup(resize_keyboard=True)
    )
    await state.set_state(Survey.start)

@router.message(Survey.start, F.text == "Так")
async def ask_age(message: types.Message, state: FSMContext):
    await state.set_state(Survey.age)
    await message.answer("Скільки вам років? (вкажіть цифрами)", reply_markup=types.ReplyKeyboardRemove())

@router.message(Survey.age)
async def ask_city(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(Survey.city)
    await message.answer("З якого ви міста?")

@router.message(Survey.city)
async def ask_schedule(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(Survey.schedule)
    await message.answer("Який варіант графіку вам більш комфортний?",
                         reply_markup=ReplyKeyboardBuilder()
                         .button(text="Денна зміна")
                         .button(text="Нічна зміна")
                         .as_markup(resize_keyboard=True))

@router.message(Survey.schedule)
async def ask_name(message: types.Message, state: FSMContext):
    await state.update_data(schedule=message.text)
    await state.set_state(Survey.name)
    await message.answer("Як вас звати?", reply_markup=types.ReplyKeyboardRemove())

@router.message(Survey.name)
async def ask_contact_info(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Survey.contact_info)
    await message.answer("Вкажіть ваш номер телефону, або нік у Телеграм та наш менеджер Валентина зв’яжеться з вами")

@router.message(Survey.contact_info)
async def complete_survey(message: types.Message, state: FSMContext):
    await state.update_data(contact_info=message.text)

    await message.answer("Дякуємо. На цьому заповнення анкети завершено.\n\n"
                         "Наступний крок – коротка співбесіда. Тривалість – до 10 хвилин.\n"
                         "Вам розкажуть основні задачі та пояснять як формується заробітна плата.\n\n"
                         "Наш менеджер зв'яжеться з вами найближчим часом, за контактами вказаними вами у заявці.",
                         reply_markup=types.ReplyKeyboardRemove())

    data = await state.get_data()
    response_message = (
        f"Нова відповідь на опитування:\n\n"
        f"User ID: {data.get('user_id')}\n"
        f"Username: @{data.get('username')}\n"
        f"\n"
        f"Age: {data.get('age')}\n"
        f"City: {data.get('city')}\n"
        f"Schedule: {data.get('schedule')}\n"
        f"Name: {data.get('name')}\n"
        f"Contact Info: {data.get('contact_info')}\n"
    )

    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=response_message)
    await state.clear()

if __name__ == "__main__":
    async def main():
        await dp.start_polling(bot, skip_updates=True)

    async def shutdown():
        await bot.session.close()

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        asyncio.run(shutdown())
