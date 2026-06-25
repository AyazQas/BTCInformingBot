from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.config import BOT_TOKEN
from app.utils.functions import back_keyb, add_group_db, get_removedb_keyb, delete_from_db, get_btc_price

router = Router()


class AddGroup(StatesGroup):
    data = State()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    if message.chat.type == 'private':
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="Добавить группу", callback_data="group_add"),
                     InlineKeyboardButton(text="Удалить группу", callback_data="group_remove"))
        keyboard.adjust(1)
        await message.answer(
            "Две функции, просмотра и добавления.\n\n",
            reply_markup=keyboard.as_markup(),
        )
    else:
        await message.answer('Бот работает в личных сообщениях.')


@router.message(Command('id'))
async def id_handler(message: Message, state: FSMContext):
    await state.clear()
    try:
        await message.delete()
    except:
        print('Выдайте права Администратора боту.')
    if message.chat.type != 'private':
        await message.answer(str(message.chat.id))
    else:
        await message.answer('Команду можно прописать только в группе')


@router.callback_query(F.data == 'back')
async def back_handler(call: CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Добавить группу", callback_data="group_add"),
                 InlineKeyboardButton(text="Удалить группу", callback_data="group_remove"))
    keyboard.adjust(1)
    await call.message.edit_text(
        text="Две функции, просмотра и добавления.\n\n",
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(F.data == 'group_add')
async def group_router(call: CallbackQuery, state: FSMContext):
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    text = ('Укажите данные группы в формате:\nID Группы, например: -1001234567890\nИнтервал отправки в минутах, например: 5\n'
            'Название группы, например: Клиенты\n\n-1001234567890\n5\nКлиенты\n\nУзнать ID Группы можно прописав /id в группе')
    keyb = InlineKeyboardBuilder()
    keyb.add(InlineKeyboardButton(text='◀ Назад', callback_data='back'))
    await call.bot.edit_message_text(text, message_id=message_id, chat_id=chat_id, reply_markup=keyb.as_markup())
    await state.update_data(message_id=call.message.message_id)
    await state.set_state(AddGroup.data)


@router.message(AddGroup.data)
async def add_group_handler(message: Message, state: FSMContext):
    data = message.text.split('\n')
    await message.delete()
    fsm_data = await state.get_data()
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=fsm_data["message_id"]
    )
    chat_id = data[0]
    interval = data[1]
    name = data[2]
    await add_group_db(chat_id, interval, name)
    await message.answer('✔ Успешно', reply_markup=back_keyb())


@router.callback_query(F.data == 'group_remove')
async def group_remove_handler(call: CallbackQuery):
    await call.message.edit_text('Выберите нужную вам группу', reply_markup=await get_removedb_keyb())


@router.callback_query(F.data.startswith('removegroup_'))
async def remove_group_handler2(call: CallbackQuery, state: FSMContext):
    await state.clear()
    chat_id = call.data.split('_')[1]
    await delete_from_db(chat_id)
    await call.message.edit_text('🔴 Удалено', reply_markup=back_keyb())


def create_bot():
    return Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"))


def create_dispatcher():
    dp = Dispatcher()
    dp.include_router(router)
    return dp
