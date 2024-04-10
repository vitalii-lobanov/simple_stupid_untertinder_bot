# Store configuration settings here
import os

CELERY_BROKER_URL = "redis://localhost:6379/0"
#DATABASE_PATH = "telegram_test_dating_bot_database.db"
REDIS_URL = "redis://localhost:6379/0"
BOT_TOKEN = os.getenv("TELEGRAM_API_KEY")
#DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
# app/config/__init__.py
#TODO: check security
DATABASE_URI = "postgresql+asyncpg://pgsql_user:mb3L*nYTg7C!eBMC@localhost:5432/dating_bot_database"

# TODO: set correct values 
NEXT_PLEASE_WAITING_TIMEOUT = 10*60*60

app_directory = os.path.dirname(os.path.abspath(__file__))
root_directory = os.path.dirname(app_directory)
downloads_path = os.path.join(root_directory, 'downloads')
if not os.path.exists(downloads_path):
    os.makedirs(downloads_path)

DOWNLOAD_PATH = downloads_path


