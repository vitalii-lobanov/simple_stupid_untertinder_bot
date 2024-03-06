# app/routers/user_router.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.handlers.tg_commands import handle_user_messages, add_user_to_database, get_user_status, update_user_status
from app.handlers.tg_commands import set_ready_to_chat, set_not_ready_to_chat, cmd_register, cmd_start

user_router = Router()


# Handler for user to set status to ready to chat
@user_router.message(Command(commands=['ready']))
async def set_user_ready_to_chat(message: types.Message):
    await set_ready_to_chat(message)


# Handler for user to set status to not ready to chat
@user_router.message(Command(commands=['notready']))
async def set_user_not_ready_to_chat(message: types.Message):
    await set_not_ready_to_chat(message)


# Registration command handler
@user_router.message(Command(commands=['register']))
async def cmd_user_register(message: types.Message, state: FSMContext):
    await cmd_register(message, state)


# Handler for user to set status to ready to chat

@user_router.message(Command(commands=['start']))
async def cmd_user_start(message: types.Message):
    await cmd_start(message)
