# app/database/engine.py
import os

from app.utils.debug import logger
from sqlalchemy import create_engine, Column, Integer, String

from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URI
from app.models.base import Base

if os.getenv("LOG_LEVEL") == "DEBUG":
    engine = create_engine(DATABASE_URI, echo=True)
else:
    engine = create_engine(DATABASE_URI, echo=False)

logger.debug("Database URI: {}".format(DATABASE_URI))
SessionLocal = sessionmaker(bind=engine)



def initialize_db():
    try:
        logger.info("Initializing the database...")

        # Import all models modules here to ensure they are known to Base
        from app.models import User, ProfileDataTieredMessage

        logger.info("Models imported successfully.")

        # Create all tables
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("All tables created successfully.")



    except Exception as e:
        logger.critical("Failed to create tables: {}".format(e), exc_info=True)
        raise

def get_db_session():
    return SessionLocal()
