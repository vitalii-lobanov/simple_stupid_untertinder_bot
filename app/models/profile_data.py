from models.base import Base
from sqlalchemy import Column, ForeignKey, Integer, BIGINT
from sqlalchemy.orm import relationship


class ProfileData(Base):
    __tablename__ = "profile_data"
    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT, ForeignKey("users.id"))
    message_id = Column(Integer, ForeignKey("messages.id"))
    profile_version = Column(Integer)

    user = relationship("User", back_populates="profile_data")
    message = relationship("Message", back_populates="profile_data")
