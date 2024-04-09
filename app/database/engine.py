# app/database/engine.py
import os

from config import DATABASE_URI
from models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.debug import logger
from utils.d_debug import d_logger
from contextlib import contextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncEngine
from functools import wraps
from contextlib import asynccontextmanager


if os.getenv("LOG_LEVEL") == "DEBUG":
    #TODO: change back to True
    engine = create_async_engine(DATABASE_URI, echo=True)
else:
    engine = create_async_engine(DATABASE_URI, echo=False)

logger.sync_debug("Database URI: {}".format(DATABASE_URI))
# __SessionLocal__ = SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#sessionmaker(bind=engine)


# def initialize_db() -> None:
#     try:
#         logger.sync_info("Initializing the database...")

#         # Import all models modules here to ensure they are known to Base
#         from models import Conversation, Message, ProfileData, User

#         logger.sync_info("Models imported successfully.")

#         # Create all tables
#         logger.sync_info("Creating tables...")
#         Base.metadata.create_all(bind=engine, checkfirst=True)
#         logger.sync_info("All tables created successfully.")

#     except Exception as e:
#         logger.sync_error("Failed to create tables: {}".format(e), exc_info=True)
#         raise

# @contextmanager
# def get_session():
#     """Provide a transactional scope around a series of operations."""
#     session = __SessionLocal__()
#     try:
#         yield session
#         session.commit()
#     except Exception as e:
#         session.rollback()
#         raise e
#     finally:
#         session.close()

# async def initialize_db():
#     async with engine.begin() as conn:
#         try:
#             # Create all tables in the metadata
#             await conn.run_sync(Base.metadata.create_all)
#         except Exception as e:
#             logger.sync_error(f"Failed to create tables, exception: {e}", exc_info=True)



async def initialize_db() -> None:
    d_logger.debug("D_logger")
    try:
        logger.sync_info("Initializing the database...")
        
        # Import all models modules here to ensure they are known to Base
        from models import Conversation, Message, ProfileData, User
        logger.sync_info("Models imported successfully.")

        # Create all tables
        logger.sync_info("Creating tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.sync_info("All tables created successfully.")
        
    except Exception as e:
        logger.sync_error("Failed to create tables: {}".format(e), exc_info=True)
        raise

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
@asynccontextmanager
async def get_session():
    d_logger.debug("D_logger")
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await logger.sync_error(f"Failed to commit session, exception: {e}", exc_info=True)
            await session.rollback()
            
            raise
        finally:
            await session.close()


def manage_db_session(func):
    d_logger.debug("D_logger")
    try:
        @wraps(func)    
        async def wrapper(*args, **kwargs):
            session_provided = 'session' in kwargs
            if (not session_provided) or (kwargs['session'] is None):
                async with get_session() as new_session:
                    kwargs['session'] = new_session
                    return await func(*args, **kwargs)
            else:
                return await func(*args, **kwargs)
    except Exception as e:
        logger.sync_error(f"Failed to create tables: {e}", exc_info=True)        
    return wrapper