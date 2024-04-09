import logging
import colorlog
from aiogram import Bot
from core.bot import bot_instance
from aiogram.fsm.context import FSMContext
import os
from core.states import UserStates
from utils.text_messages import message_this_is_bot_message
import bleach


#We cannot import 'send_service_message' from 'telegram_messaging' module
async  def __send_service_message__(
    message: str, state: FSMContext = None, chat_id: int = None
) -> None:
    if state is not None:
        tg_chat_id = state.key.chat_id
    elif chat_id is not None:
        tg_chat_id = chat_id
    else:
        tg_chat_id = None
        raise ValueError("Either state or chat_id must be provided")
    msg = f"{message_this_is_bot_message()}{message}"
    msg = bleach.clean(msg)
    await bot_instance.send_message(chat_id=tg_chat_id, text=msg, parse_mode="HTML")
   

m_colored_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)-90s "
        "%(white)s%(bg_blue)s%(asctime)s | %(module)s.%(funcName)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )

class CustomColorLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        # TODO: check whether it considers the log level from the envinronment
        super().__init__(name, level)
        colored_formatter = m_colored_formatter

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(colored_formatter)
        self.addHandler(stream_handler)
        self.forward_messages_to_tg_users = (
            os.getenv("FORWARD_DEBUG_MESSAGES_TO_USERS", "False").upper() == "TRUE"
        )

    async def __send_msg_to_user__(
        self, msg, state: FSMContext = None, chat_id: int = None
    ):
        message = f"{msg}"
        if state is not None:
            await __send_service_message__(message=message, state=state)
        elif chat_id is not None:
            await __send_service_message__(message=message, chat_id=chat_id)
        else:
            return

    async def debug(
        self, msg, state: FSMContext = None, chat_id: int = None, exc_info=False, *args, **kwargs
    ):
        if self.forward_messages_to_tg_users:
            await self.__send_msg_to_user__(msg=msg, state=state, chat_id=chat_id)
        self._log(
            logging.DEBUG,
            msg,
            args,
            exc_info=None,
            extra=None,
            stack_info=False,
            stacklevel=2,
            **kwargs,
        )

    def sync_debug(self, msg,  exc_info=False, *args, **kwargs):
        self._log(
            logging.DEBUG,
            msg,
            args,
            exc_info=exc_info,
            extra=None,
            stack_info=False,
            stacklevel=2,
            **kwargs,
        )

    async def info(
        self, msg, state: FSMContext = None, chat_id: int = None, exc_info=False, *args, **kwargs
    ):
        if self.forward_messages_to_tg_users:
            await self.__send_msg_to_user__(msg=msg, state=state, chat_id=chat_id)
        self._log(
            logging.INFO,
            msg,
            args,
            exc_info=exc_info,
            extra=None,
            stack_info=False,
            stacklevel=2,
            **kwargs,
        )

    def sync_info(self, msg, exc_info=False, *args, **kwargs):
        self._log(
            logging.INFO,
            msg,
            args,
            exc_info=exc_info,
            extra=None,
            stack_info=False,
            stacklevel=2,
            **kwargs,
        )

    async def warning(
        self, msg, state: FSMContext = None, chat_id: int = None, exc_info=False, *args, **kwargs
    ):
        if self.forward_messages_to_tg_users:
            await self.__send_msg_to_user__(msg=msg, state=state, chat_id=chat_id)
        self._log(
            logging.WARNING,
            msg,
            args,
            exc_info=exc_info,
            extra=None,
            stack_info=False,
            stacklevel=2,
            **kwargs,
        )

    def sync_warning(self, msg, exc_info=False, *args, **kwargs):
        self._log(
            logging.WARNING,
            msg,
            args,
            exc_info=exc_info,
            extra=None,
            stack_info=False,
            stacklevel=2,
            **kwargs,
        )

    async def error(
        self, msg, exc_info=False, state: FSMContext = None, chat_id: int = None, *args, **kwargs
    ):
        if self.forward_messages_to_tg_users:
            await self.__send_msg_to_user__(msg=msg, state=state, chat_id=chat_id)
        self._log(
            logging.ERROR,
            msg,
            args,
            exc_info=exc_info,
            extra=None,
            stack_info=False,
            stacklevel=2,
            **kwargs,
        )

    def sync_error(self, msg, exc_info=False, *args, **kwargs):
        self._log(
            logging.ERROR,
            msg,
            args,
            exc_info=exc_info,
            extra=None,
            stack_info=False,
            stacklevel=2,
            **kwargs,
        )

    async def critical(
        self, msg, state: FSMContext = None, chat_id: int = None, exc_info=False, *args, **kwargs
    ):
        if self.forward_messages_to_tg_users:
            await self.__send_msg_to_user__(msg=msg, state=state, chat_id=chat_id)
        self._log(
            logging.CRITICAL,
            msg,
            args,
            exc_info=exc_info,
            extra=None,
            stack_info=False,
            stacklevel=2,
            **kwargs,
        )

    def sync_critical(self, msg, exc_info=False, *args, **kwargs):
        self._log(
            logging.CRITICAL,
            msg,
            args,
            exc_info=exc_info,
            extra=None,
            stack_info=False,
            stacklevel=2,
            **kwargs,
        )

logger = CustomColorLogger(name="CustomLogger")







