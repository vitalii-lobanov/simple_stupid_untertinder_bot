from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import Base

class Reaction(Base):
    __tablename__ = 'reactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))    
    sender_message_id = Column(Integer, ForeignKey('messages.id'))
    new_emoji = Column(String, default=None)
    old_emoji = Column(String, default=None)
    timestamp = Column(DateTime, default=None)
    receiver_message_id = Column(Integer, default=None)
    rank = Column(Integer, default=0)

    user = relationship('User')
    # The backref 'message' here allows us to access the message from a Reaction instance
    #message = relationship('Message', backref='reactions')
    #message = relationship('Message', backref='message_reactions', foreign_keys=[sender_message_id])
    #message = relationship('Message', backref='reactions', foreign_keys=[sender_message_id])
    #message = relationship('Message', backref='message_reactions', foreign_keys=[sender_message_id])
    # Ensure backref is a unique name, not used anywhere else as a property in the Message model
    message = relationship('Message', backref='message_reactions', foreign_keys=[sender_message_id])