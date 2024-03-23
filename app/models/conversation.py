from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.base import Base

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    user1_id = Column(Integer, ForeignKey('users.id'))
    user1_profile_version = Column(Integer)
    user2_id = Column(Integer, ForeignKey('users.id'))    
    user2_profile_version = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True, default=None)
    is_active = Column(Boolean, default=True, nullable=False)
    user1 = relationship('User', foreign_keys=[user1_id])
    user2 = relationship('User', foreign_keys=[user2_id])
    
    messages = relationship("Message", back_populates="conversation")