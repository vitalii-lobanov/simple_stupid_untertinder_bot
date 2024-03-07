from sqlalchemy import Column, Integer, String, Boolean
from app.models.base import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    is_active = Column(Boolean, default=True)  # Add this line
    #messages = relationship('Message', back_populates='user')