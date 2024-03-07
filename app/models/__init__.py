from sqlalchemy.orm import relationship

from app.utils.debug import logger

from app.models.base import Base
from app.models.user import User
from app.models.message import Message

# Define cross-model relationships here if needed
User.messages = relationship('Message', order_by=Message.id, back_populates='user')