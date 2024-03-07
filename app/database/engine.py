# app/database/engine.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import DATABASE_URI
from app.utils.debug import logger
Base = declarative_base()
engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)

def initialize_db():
    # Import all models modules here to ensure they are known to Base
    from app.models import user  # Assuming you have a user module within the models package
    # Create all tables
    Base.metadata.create_all(bind=engine)
def get_db_session():
    return SessionLocal()


