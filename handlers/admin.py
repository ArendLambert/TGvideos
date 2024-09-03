import aiogram.utils.keyboard
from aiogram import types, Router, F, Bot
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from PostgreSQL.database import DataBase

database = DataBase()
series = ["BAACAgIAAxkBAAORZWuPbG6aQEzR4LSpLi7B6eT_g3IAAoA9AAKyCmBLp4tdMccv1ngzBA",
          "BAACAgIAAxkBAAOnZWuSt1J2TsFQPvgj-s_pl0A7494AAvY9AAKyCmBLECrP_SlU6S8zBA",
          "BAACAgIAAxkBAAOVZWuPqIh1rUioBbQdgGhwggHzRpQAAtk9AAKyCmBLERlc8k1PNKMzBA",
          "BAACAgIAAxkBAAOXZWuPva5tBhSCo_hB3taqVUIsj2cAAkg9AAKyCmBLrlDMmiJsm9YzBA",
          "BAACAgIAAxkBAAOZZWuPzX5exU0ktMOz8vq4ceWa7FgAAtM9AAKyCmBLmHt6tyzzFWkzBA"]

admins = ['1777911166', '581271086']


class AdminPanel(StatesGroup):
    admin = State()
    new_post = State()
    new_post_step_two = State()
    post_text = ''


router = Router()
router.message.filter()


def get_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        types.InlineKeyboardButton(text=f"Серия {i+1}", callback_data=f"series_{i+1}") for i in range(0, len(series))
    ]
    builder = InlineKeyboardBuilder()
    builder.row(*(button for button in buttons), width=2)
    builder.row(types.InlineKeyboardButton(text="Телеграм канал со всеми сериями",
                                           url="https://t.me/ScorlupaChannel"))
    return builder.as_markup()


@router.message(Command("AllUsers"), AdminPanel.admin)
async def new_post(message: types.Message, state: FSMContext) -> None:
    all_users_list = database.select_id_from_database('users')
    mailing_users_list = database.select_id_from_database('mailing_users')
    text_message = 'Все пользователи:\n'
    for row in all_users_list:
        text_message += f"{row[0]}   {row[1]}\n"
    text_message += "\n\n\nПользователи для рассылки:\n"
    for row in mailing_users_list:
        text_message += f"{row[0]}   {row[1]}\n"
    await message.answer(text_message)


@router.message(Command("NewPost"), AdminPanel.admin)
async def new_post(message: types.Message, state: FSMContext) -> None:
    await message.answer("Текст поста:")
    await state.set_state(AdminPanel.new_post)


@router.message(F.text, AdminPanel.new_post)
async def new_post_step_one(message: types.Message, state: FSMContext) -> None:
    await message.answer(message.text)
    AdminPanel.post_text = message.text
    await message.answer("/Advertising для рекламного поста\n/Notification - для поста-оповещения\n"
                         "/Exit для выхода")
    await state.set_state(AdminPanel.new_post_step_two)


@router.message(Command("Notification"), AdminPanel.new_post_step_two)
async def new_post_mailing(message: types.Message, state: FSMContext, bot: Bot) -> None:
    mailing_users_list = database.select_id_from_database('mailing_users')
    for user_data in mailing_users_list:
        await bot.send_message(user_data[0], f'{user_data[1]}, {AdminPanel.post_text}')
    await state.set_state(AdminPanel.admin)
    await message.answer("Вы в одмин панели\n/NewPost - для нового поста\n/AllUsers - для "
                         "получения списка пользователей")


@router.message(Command("Advertising"), AdminPanel.new_post_step_two)
async def new_post_mailing(message: types.Message, state: FSMContext, bot: Bot) -> None:
    all_users_list = database.select_id_from_database('users')
    for user_data in all_users_list:
        await bot.send_message(user_data[0], f'{user_data[1]}, {AdminPanel.post_text}')
    await state.set_state(AdminPanel.admin)
    await message.answer("Вы в одмин панели\n/NewPost - для нового поста\n/AllUsers - для "
                         "получения списка пользователей")


@router.message(Command("Exit"))
async def exit_from_admin(message: types.Message, state: FSMContext) -> None:
    await message.answer("Вы покинули одминку")
    await state.clear()


@router.message(AdminPanel.admin, F.video)
async def start(message: types.Message) -> None:
    await message.answer(message.video.file_id)

