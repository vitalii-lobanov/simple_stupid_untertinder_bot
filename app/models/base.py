from sqlalchemy.orm import declarative_base
from enum import Enum
Base = declarative_base()

class MessageSource(Enum):
    registration_profile = 1
    conversation = 2

