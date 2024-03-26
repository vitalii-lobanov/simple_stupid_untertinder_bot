from sqlalchemy import Column, Integer, String, Boolean
from models.base import Base
from sqlalchemy.orm import relationship
from models.message import Message
from models.profile_data import ProfileData


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    is_ready_to_chat = Column(Boolean, default=False)
    messages = relationship("Message", order_by=Message.id, back_populates="sender")
    profile_version = Column(Integer)

    profile_data = relationship(
        "ProfileData", order_by=ProfileData.id, back_populates="user"
    )
