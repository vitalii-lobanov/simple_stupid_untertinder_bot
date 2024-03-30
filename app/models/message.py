from models.base import Base, MessageSource
from models.profile_data import ProfileData
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    BIGINT
)
from sqlalchemy.orm import relationship


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT, ForeignKey("users.id"))
    tg_message_id = Column(Integer)
    message_source = Column(Enum(MessageSource))
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    text = Column(String)
    user_profile_version = Column(Integer)
    timestamp = Column(DateTime)
    tier = Column(Integer)

    audio = Column(String)
    video = Column(String)
    sticker = Column(String)
    voice = Column(String)
    video_note = Column(String)
    from_user = Column(JSON)
    animation = Column(String)    
    image = Column(String)
    photo = Column(String)

    document = Column(String)
    other_content = Column(JSON)    
    author_signature = Column(String)
    caption = Column(String)
    caption_entities = Column(JSON)
    contact = Column(JSON)
    forward_date = Column(Integer)    
    dice = Column(JSON)    
    entities = Column(JSON)
    game = Column(JSON)
    html_text = Column(String)
    invoice = Column(JSON)
    location = Column(JSON)
    link_preview_options = Column(JSON)
    md_text = Column(String)
    media_group_id = Column(String)
    
    poll = Column(JSON)
    quote = Column(JSON)
    
    story = Column(JSON) 

    original_sender_id = Column(Integer)
    original_sender_username = Column(String)
    sender_in_conversation_id = Column(BIGINT)

    user = relationship("User", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")
    profile_data = relationship(
        "ProfileData", order_by=ProfileData.id, back_populates="message"
    )
    # # reactions = relationship(
    # #     "Reaction", backref="message_reactions", foreign_keys="[Reaction.tg_message_id]"
    # # )
    # reactions = relationship(
    #     "Reaction",
    #     back_populates="message",
    #     foreign_keys="[Reaction.tg_message_id]"
    # )

    # reactions = relationship(
    #     "Reaction", backref="message", foreign_keys="[Reaction.sender_message_id]"
    # )

    reactions = relationship("Reaction", back_populates="message")