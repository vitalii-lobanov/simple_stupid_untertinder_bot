from celery import shared_task
from sqlalchemy.orm import Session
from database.engine import SessionLocal
from models.user import User
from states import UserStates
from aiogram import Bot

@shared_task
def match_users():
    session: Session = SessionLocal()
    try:
        # Find users who are ready to chat but not in a conversation
        users_ready = session.query(User).filter(User.is_ready_to_chat == True, User.is_active == True).all()

        # Matchmaking logic (simple version: just pair the first two users)
        if len(users_ready) >= 2:
            alice = users_ready[0]
            bob = users_ready[1]

            # Update their states to chatting_in_progress
            alice.is_ready_to_chat = False
            bob.is_ready_to_chat = False

            # You might also want to create a Conversation object or similar here

            session.commit()

            # Send notifications (example using aiogram)
            bot = Bot(token="your-bot-token")
            asyncio.run(bot.send_message(alice.id, "You've been matched! Start chatting."))
            asyncio.run(bot.send_message(bob.id, "You've been matched! Start chatting."))
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

from celery import Celery
from celery.schedules import crontab

app = Celery('myapp', broker='your_broker_url')

app.conf.beat_schedule = {
    'match-users-every-minute': {
        'task': 'app.tasks.match_users.match_users',
        'schedule': crontab(minute='*'),
    },
}