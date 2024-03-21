from aiogram import Bot
from aiogram.fsm.context import FSMContext
from utils.text_messages import message_this_is_bot_message

async def send_service_message(bot_instance: Bot, message: str, state: FSMContext = None, chat_id: int = None):
    if state is not None:
        tg_chat_id = state.key.chat_id
    elif chat_id is not None:
        tg_chat_id = chat_id
    else:
        tg_chat_id = None
        raise ValueError('Either state or chat_id must be provided')
    msg = f'{message_this_is_bot_message()}{message}'         
    await bot_instance.send_message(chat_id=tg_chat_id, text=msg, parse_mode='HTML')