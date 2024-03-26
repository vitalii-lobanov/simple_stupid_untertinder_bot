from models.base import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Reaction(Base):
    __tablename__ = "reactions"
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    sender_message_id = Column(Integer, default=None)
    new_emoji = Column(String, default=None)
    old_emoji = Column(String, default=None)
    timestamp = Column(DateTime, default=None)
    receiver_message_id = Column(Integer, default=None)
    rank = Column(Integer, default=0)

    user = relationship("User")
    #message = relationship("Message", backref="emoji_reactions")
    message = relationship(
        "Message",
        back_populates="reactions",
        foreign_keys=[message_id]
    )
    