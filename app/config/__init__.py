# Store configuration settings here
import os

CELERY_BROKER_URL = 'redis://localhost:6379/0'
DATABASE_PATH = 'telegram_test_dating_bot_database.db'
REDIS_URL = 'redis://localhost:6379/0'
BOT_TOKEN = os.getenv("TELEGRAM_API_KEY")
DATABASE_URI = f"sqlite:///{DATABASE_PATH}"

