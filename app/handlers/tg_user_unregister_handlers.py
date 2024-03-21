from database.engine import SessionLocal
from models.user import User
from utils.debug import logger
from aiogram import types


async def cmd_unregister(message: types.Message):
    user_id = message.from_user.id

    session = SessionLocal()
    try:
        existing_user = session.query(User).filter_by(id=user_id).first()
        if existing_user and existing_user.is_active:
            # Mark the user as inactive instead of deleting
            existing_user.is_active = False
            session.commit()
            await message.answer("You have been unregistered successfully.")
        else:
            # The user is not registered or already inactive
            await message.answer("You are not registered or already unregistered.")
    except Exception as e:
        session.rollback()
        await message.answer("Unregistration failed.")
        await logger.error(msg=f"Unregistration failed: {str(e)}", chat_id=user_id)
        # Log the exception or handle it as necessary
    finally:
        session.close()


async def cmd_hard_unregister(message: types.Message):
    user_id = message.from_user.id
    logger.sync_debug(f"Trying to unregister user: {user_id}")
    # Create a new database session
    session = SessionLocal()
    try:
        # Retrieve the user profile
        user_profile = session.query(User).filter_by(id=user_id).first()
        if user_profile:
            # Delete any related data here, for example, user messages, settings, etc.
            # session.query(RelatedModel).filter_by(user_id=user_id).delete()

            # Delete the user profile
            session.delete(user_profile)
            session.commit()
            await message.answer("Your profile and all associated data have been permanently deleted.")
        else:
            await message.answer("You do not have a profile to delete.")
    except Exception as e:
        session.rollback()
        await message.answer("Failed to unregister. Please try again later.")
        print(str(e))
        # Log the exception or handle it as necessary
    finally:
        session.close()
