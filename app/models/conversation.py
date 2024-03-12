from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    user1_id = Column(Integer, ForeignKey('users.id'))
    user2_id = Column(Integer, ForeignKey('users.id'))
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    
    user1 = relationship('User', foreign_keys=[user1_id])
    user2 = relationship('User', foreign_keys=[user2_id])
    
    messages = relationship("Message", back_populates="conversation")