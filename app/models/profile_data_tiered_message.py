from sqlalchemy import Column, Integer, ForeignKey, String, Text, LargeBinary, JSON
from sqlalchemy.orm import relationship
from models.base import Base


class ProfileDataTieredMessage(Base):
    __tablename__ = 'profile_data_tiered_messages'

    # Assuming 'id' is intended to be the primary key
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    tier = Column(Integer)
    text = Column(String)
    audio = Column(LargeBinary)
    video = Column(LargeBinary)
    image = Column(LargeBinary)
    document = Column(LargeBinary)
    other_content = Column(JSON)
    document = Column(LargeBinary)
    animation = Column(LargeBinary)
    author_signature = Column(String)
    caption = Column(String)
    caption_entities = Column(JSON)
    contact = Column(JSON)            
    forward_date = Column(Integer)
    from_user = Column(LargeBinary)
    game = Column(JSON)
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
    photo = Column(JSON)
    poll = Column(JSON)
    quote = Column(JSON)
    sticker = Column(JSON)
    story = Column(JSON)
    text = Column(String)
    voice = Column(LargeBinary)
    video_note = Column(LargeBinary)
    video = Column(LargeBinary)


    # Relationship to the User model
    user = relationship('User', back_populates='profile_data_tiered_messages')