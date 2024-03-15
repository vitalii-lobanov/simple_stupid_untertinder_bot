
from models.base import Base, MessageSource
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, LargeBinary, String, Enum
from sqlalchemy.orm import relationship


class Message(Base):
    __tablename__ = 'messages'     
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message_source = Column(Enum(MessageSource))
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=True)    
    timestamp = Column(DateTime)  
    tier = Column(Integer)    
    audio = Column(LargeBinary)
    video = Column(LargeBinary)
    image = Column(LargeBinary)    
    other_content = Column(JSON)    
    animation = Column(LargeBinary)
    author_signature = Column(String)
    caption = Column(String)
    caption_entities = Column(JSON)
    contact = Column(JSON)            
    forward_date = Column(Integer)
    from_user = Column(LargeBinary)    
    dice = Column(JSON)
    document = Column(LargeBinary)
    entities = Column(JSON)
    game = Column(JSON)
    html_text = Column(String)
    invoice = Column(JSON)
    location = Column(JSON)
    link_preview_options = Column(JSON)
    md_text = Column(String)
    media_group_id = Column(String)
    photo = Column(String)
    poll = Column(JSON)
    quote = Column(JSON)
    sticker = Column(LargeBinary)
    story = Column(JSON)
    text = Column(String)
    voice = Column(LargeBinary)
    video_note = Column(LargeBinary)
    video = Column(LargeBinary)
    original_sender_id = Column(Integer)
    original_sender_username = Column(String) 
    
    user = relationship('User', back_populates='messages')
    conversation = relationship('Conversation', back_populates='messages')




