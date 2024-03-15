from sqlalchemy.orm import relationship


from models.user import User
from models.conversation import Conversation
from models.message import Message

# If you have additional cross-model relationships to define, do it here
# For example, if the relationships are not defined within the model classes themselves
User.messages = relationship('Message', order_by=Message.id, back_populates='user')
Conversation.messages = relationship('Message', order_by=Message.id, back_populates='conversation')