# app/database/engine.py
import os

from config import DATABASE_URI
from models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.debug import logger
from contextlib import contextmanager

if os.getenv("LOG_LEVEL") == "DEBUG":
    engine = create_engine(DATABASE_URI, echo=True)
else:
    engine = create_engine(DATABASE_URI, echo=False)

logger.sync_debug("Database URI: {}".format(DATABASE_URI))
__SessionLocal__ = SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#sessionmaker(bind=engine)


def initialize_db() -> None:
    try:
        logger.sync_info("Initializing the database...")

        # Import all models modules here to ensure they are known to Base
        from models import Conversation, Message, ProfileData, User

        logger.sync_info("Models imported successfully.")

        # Create all tables
        logger.sync_info("Creating tables...")
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.sync_info("All tables created successfully.")

    except Exception as e:
        logger.sync_error("Failed to create tables: {}".format(e), exc_info=True)
        raise

@contextmanager
def get_session():
    """Provide a transactional scope around a series of operations."""
    session = __SessionLocal__()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# def get_db_session():
#     return SessionLocal()
