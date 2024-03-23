from database.engine import SessionLocal
from models.user import User
from utils.debug import logger
from aiogram import types
from handlers.tg_commands import cmd_start, cmd_unregister, cmd_hard_unregister

#TODO: Put hard_unregister / hard_unregister versioning helpers here