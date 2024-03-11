from sqlalchemy.orm import relationship

from utils.debug import logger

from models.base import Base
from models.user import User
from models.profile_data_tiered_message import ProfileDataTieredMessage

# Define cross-model relationships here if needed
User.profile_data_tiered_messages = relationship('ProfileDataTieredMessage', order_by=ProfileDataTieredMessage.id, back_populates='user')