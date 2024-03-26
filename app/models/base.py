from enum import Enum

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MessageSource(Enum):
    registration_profile = 1
    conversation = 2
    command_received = 3
    bot_message_received = 4
