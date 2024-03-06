# app/models/message.py
from sqlalchemy import Column, Integer, ForeignKey, String, LargeBinary
from sqlalchemy.orm import relationship
from app.database.engine import Base


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    text = Column(String)  # For text messages
    audio = Column(LargeBinary)  # For audio files
    video = Column(LargeBinary)  # For video files
    image = Column(LargeBinary)  # For image files

    # Define relationships
    user = relationship('User', back_populates='messages')
    # Add more fields as necessary for reactions, etc.



