# app/routers/user_router.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.handlers.tg_commands import handle_user_messages, add_user_to_database, get_user_status, update_user_status
from app.handlers.tg_commands import set_ready_to_chat, set_not_ready_to_chat, cmd_register, cmd_start
from app.handlers.tg_commands import cmd_unregister, message_reaction_handler, cmd_hard_unregister
from aiogram import Dispatcher, types

bot_instance = None

def setup_router(bot):
    global bot_instance
    bot_instance = bot


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

@user_router.message(Command(commands=['unregister']))
async def cmd_user_unregister(message: types.Message, state: FSMContext):
    await cmd_unregister(message)
# Handler for user to set status to ready to chat

@user_router.message(Command(commands=['start']))
async def cmd_user_start(message: types.Message):
    await cmd_start(message)

@user_router.message(Command(commands=['hard_unregister']))
async def cmd_user_hard_unregister(message: types.Message):
    await cmd_hard_unregister(message)



#Default handler for all other messages
@user_router.message_reaction()
async def message_user_reaction_handler(message_reaction: types.MessageReactionUpdated):
    await message_reaction_handler(message_reaction)
