# from celery import shared_task
# from utils.debug import logger
# from sqlalchemy.orm import Session
# from database.engine import SessionLocal
# from models.user import User
# from states import UserStates
# from aiogram import Bot
# import random
# from models import Conversation
# from bot import bot_instance
# import asyncio
# from aiogram.dispatcher import FSMContext
# from bot import bot_instance


# async def send_match_notification(user_id: int, message_text: str):
#     try:
#         await bot_instance.send_message(chat_id=user_id, text=message_text)
#     except Exception as e:
#         logger.critical(f"Failed to send a message to {user_id}: {str(e)}")


# @shared_task
# def match_users():
#     session: Session = SessionLocal()
#     try:
#         # Find users who are ready to chat but not in a conversation
#         users_ready = session.query(User).filter(User.is_ready_to_chat == True, User.is_active == True).all()
#         # Shuffle the list of users to randomize pairing
#         random.shuffle(users_ready)

#         # Matchmaking logic (simple version: just pair the first two users)
#         if len(users_ready) >= 2:
#             user_1 = users_ready[0]
#             user_2 = users_ready[1]

#             # Update their states to chatting_in_progress
#             user_1.is_ready_to_chat = False
#             user_2.is_ready_to_chat = False

#             # You might also want to create a Conversation object or similar here
#             conversation = Conversation(user1_id=user_1.id, user2_id=user_2.id)

#             storage = bot_instance.get("storage")

#             alice_context = FSMContext(dispatcher.storage, alice_user_id, alice_chat_id)

#             # Change Alice's FSM state
#             await alice_context.set_state(SomeState)

#             session.add(conversation)
#             session.commit()            
            
#             loop = asyncio.get_event_loop()
#             loop.run_until_complete(send_match_notification(user_1.id, "You've been matched! Start chatting."))
#             loop.run_until_complete(send_match_notification(user_2.id, "You've been matched! Start chatting."))


#     except Exception as e:
#         session.rollback()
#         logger.critical(f'Caught exception in match_users Celery task: {str(e)}')
#         raise e
#     finally:
#         session.close()

# from celery import Celery
# from celery.schedules import crontab
# from celery_helpers.celery_app import celery_app



# celery_app.conf.beat_schedule = {
#     'match-users-every-minute': {
#         'task': 'app.tasks.match_users.match_users',
#         'schedule': crontab(minute='*'),
#     },
# }