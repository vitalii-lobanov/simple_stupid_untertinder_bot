from sqlalchemy.orm import relationship

from app.utils.debug import logger

from app.models.base import Base
from app.models.user import User
from app.models.profile_data_tiered_message import ProfileDataTieredMessage

# Define cross-model relationships here if needed
User.profile_data_tiered_messages = relationship('ProfileDataTieredMessage', order_by=ProfileDataTieredMessage.id, back_populates='user')