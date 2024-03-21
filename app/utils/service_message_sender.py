from aiogram import Bot
from aiogram.fsm import FSMContext

class ServiceMessageSender():
    def __init__(self, bot_instance: Bot, state: FSMContext):
        self.bot_instance = bot_instance
        self.chat_id = state.get_data()['chat_id']

    def send_message(self, message):
        self.bot_instance.send_message(chat_id=self.chat_id, text=message)

