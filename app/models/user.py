from sqlalchemy import Column, Integer, String, Boolean
from models.base import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    is_ready_to_chat = Column(Boolean, default=False)
    profile_data_tiered_messages = relationship('ProfileDataTieredMessage', back_populates='user')