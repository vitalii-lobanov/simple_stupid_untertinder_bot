# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database.engine import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database.engine import Base
from app.utils.debug import logger
# Make sure to import the Message class
from app.models.message import Message




class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    is_active = Column(Boolean, default=True)  # Add this line
    messages = relationship('Message', back_populates='user')