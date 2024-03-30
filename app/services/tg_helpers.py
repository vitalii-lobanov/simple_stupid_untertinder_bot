from core.bot import bot_instance
from aiogram.types import File
from config import DOWNLOAD_PATH
import os
import uuid
from aiogram.exceptions import TelegramBadRequest
from utils.text_messages import message_file_is_too_large_use_files_less_20_MB
from utils.debug import logger
#from core.telegram_messaging import send_service_message

async def get_telegram_file(file_id: str) -> File:
    try:
        file = await bot_instance.get_file(file_id)
        return File(path=file.file_path)
    except TelegramBadRequest as e:
        logger.sync_error(msg=f"Error getting file, BAD REQUEST: {e}")
        raise e    
    

async def download_telegram_file(file_id: str = None, chat_id: int = None) -> str:
    try:
        file = await get_telegram_file(file_id=file_id) 
        file_path = file.file_path
        unique_filename = f"{uuid.uuid4()}_{os.path.basename(file_id)}"
        destination = os.path.join(DOWNLOAD_PATH, unique_filename)
        await bot_instance.download_file(file_path=file_path, destination=destination)
        return destination
    except TelegramBadRequest as e:
        #send_service_message(message=message_file_is_too_large_use_files_less_20_MB(), chat_id=chat_id)
        logger.sync_error(msg=f"Error downloading file, BAD REQUEST: {e}")
        return None
    except Exception as e:
        logger.sync_error(msg=f"Error downloading file: {e}")
        return None
        
        