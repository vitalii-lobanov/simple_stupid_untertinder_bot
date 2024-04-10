# TODO: move contents of service_message_sender.py to here

from aiogram import types
# from app.tasks.tasks import celery_app
from utils.debug import logger
from utils.d_debug import d_logger

from sqlalchemy.ext.asyncio import AsyncSession


from core.telegram_messaging import send_reconstructed_telegram_message_to_user
from database.engine import manage_db_session
from services.dao import (
    get_tiered_profile_message_from_db,
    get_max_profile_version_of_user_from_db,
)

@manage_db_session
async def send_tiered_partner_s_message_to_user(        
    user_id: int = 0,
    partner_id: int = 0,
    tier: int = -1,
    session: AsyncSession = None,
) -> None:
   
    try:        
        current_partner_profile_version = await get_max_profile_version_of_user_from_db(
            user_id=partner_id
        )
        # #TODO: WTF? How id related to current_partner_profile_version???
        # if current_partner_profile_version == 0:
        #     id = user_id            
        # else:
        #     id = partner_id

        id = partner_id
        profile_version = current_partner_profile_version
        
        tiered_message = await get_tiered_profile_message_from_db(
            session=session,
            user_id=id,
            tier=tier,
            profile_version=profile_version,            
        )

        await send_reconstructed_telegram_message_to_user(
            message=tiered_message, user_id=user_id
        )
    except Exception as e:
        logger.sync_error(msg=f"Error sending tiered profile message: {e}")
        raise e

