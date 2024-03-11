# from celery import Celery
# from config import CELERY_BROKER_URL
# from database.engine import SessionLocal
# from models.profile_data_tiered_message import Message
# from utils.debug import logger
#
# # Initialize Celery
# celery_app = Celery('tasks', broker=CELERY_BROKER_URL)
#
# # maybe change to call function from somewhere else
#
# # @celery_app.task
# # def save_registration_message_task(user_id: int, message_text: str):
# #     session = SessionLocal()
# #     try:
# #         new_message = Message(user_id=user_id, text=message_text)
# #         session.add(new_message)
# #         session.commit()
# #     except Exception as e:
# #         session.rollback()
# #         logger.critical(f"Failed to save message: {e}")
# #     finally:
# #         session.close()