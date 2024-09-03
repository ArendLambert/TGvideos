from aiogram.fsm.context import FSMContext
from handlers.admin import get_keyboard, series, AdminPanel, admins
from aiogram.filters import Command
from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.config import voice
from PostgreSQL.database import DataBase
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.types import ChatMemberUpdated

database = DataBase()
router = Router()
router.message.filter()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    database.delete_row(event.from_user.id, 'mailing_users')
    database.delete_row(event.from_user.id, 'users')


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    database.insert_data_to_database(event.chat.id, event.from_user.username, 'mailing_users')
    database.insert_data_to_database(event.chat.id, event.from_user.username, 'users')


@router.message(Command("start"))
async def start(message: types.Message) -> None:
    database.insert_data_to_database(message.from_user.id, message.from_user.first_name, 'users')
    database.insert_data_to_database(message.from_user.id, message.from_user.first_name, 'mailing_users')
    builder = InlineKeyboardBuilder()
    buttons = [types.InlineKeyboardButton(text="Выбрать серию", callback_data="choose"),
               types.InlineKeyboardButton(text="Вкл./Откл. оповещения о новый сериях", callback_data="switch_mailing"),
               types.InlineKeyboardButton(text="Телеграм канал со всеми сериями", url="https://t.me/ScorlupaChannel")]
    builder.row(*(button for button in buttons), width = 1)
    await message.answer_voice(voice, reply_markup=builder.as_markup())


@router.callback_query(F.data == "choose")
async def choose_series_inline(callback: types.CallbackQuery):
    await callback.message.answer(text="Выберите серию:", reply_markup=get_keyboard())


@router.message(Command("series"))
async def choose_series_inline(message: types.Message):
    await message.answer(text="Выберите серию:", reply_markup=get_keyboard())


@router.callback_query(F.data == "switch_mailing")
async def choose_series_inline(callback: types.CallbackQuery):
    mailing_users_list = database.select_id_from_database('mailing_users')
    for user_data in mailing_users_list:
        if callback.message.chat.id == user_data[0]:
            database.delete_row(callback.message.chat.id, 'mailing_users')
            await callback.message.answer(text="Вы отключили уведомления")
            break
    else:
        database.insert_data_to_database(callback.message.chat.id, callback.message.chat.first_name, 'mailing_users')
        await callback.message.answer(text="Вы включили уведомления")


@router.callback_query(F.data.startswith("series_"))
async def choose_series_inline(callback: types.CallbackQuery):
    num = int(callback.data.split("_")[1])
    await callback.message.answer_video(series[num - 1])
    await callback.message.answer(f"Приятного просмотра {num} серии🍿")


@router.message(Command("Admin"))
async def new_post(message: types.Message, state: FSMContext) -> None:
    for admin in admins:
        if str(message.from_user.id) == admin:
            await state.set_state(AdminPanel.admin)
            await message.answer("Вы попали в одмин панель\n/NewPost - для нового поста\n/AllUsers - для "
                                 "получения списка пользователей")
