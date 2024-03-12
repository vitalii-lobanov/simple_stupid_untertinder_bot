from celery import Celery
from config import CELERY_BROKER_URL

# Initialize Celery
celery_app = Celery('tasks', broker=CELERY_BROKER_URL)

#TODO: CELERY ENQUEUE TASKS