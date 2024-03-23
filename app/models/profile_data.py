from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from models.base import Base

class ProfileData(Base):
    __tablename__ = 'profile_data'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message_id = Column(Integer, ForeignKey('messages.id'))
    profile_version = Column(Integer)

    user = relationship('User', back_populates='profile_data')
    message = relationship('Message', back_populates='profile_data')

    
    
    