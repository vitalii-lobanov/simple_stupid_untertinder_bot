from sqlalchemy.orm import relationship


from models.user import User
from models.conversation import Conversation
from models.message import Message
from models.profile_data import ProfileData

# If you have additional cross-model relationships to define, do it here
# For example, if the relationships are not defined within the model classes themselves
User.messages = relationship("Message", order_by=Message.id, back_populates="user")
Conversation.messages = relationship(
    "Message", order_by=Message.id, back_populates="conversation"
)

# Assuming you want to define relationships for ProfileData here as well
User.profile_data = relationship(
    "ProfileData", order_by=ProfileData.id, back_populates="user"
)
Message.profile_data = relationship(
    "ProfileData", order_by=ProfileData.id, back_populates="message"
)
