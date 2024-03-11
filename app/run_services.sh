#!/bin/bash

cd /Users/vitaliy_lobanov/Documents/_develop/u-social-network/dd_test_u_bot_simple/
source /Users/vitaliy_lobanov/Documents/_develop/u-social-network/dd_test_u_bot_simple/bot-venv/bin/activate

# Set the TELEGRAM_API_KEY environment variable
export TELEGRAM_API_KEY='6910899160:AAEABnf-OSCV3mA04uNYeYRcJ9_PD69ufZ0'

# Append the ./app directory to the PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PYTHONPATH="${PYTHONPATH}:./app"


# Check if Redis server is running
if redis-cli ping > /dev/null 2>&1; then
    echo "Redis is running."
else
    echo "Starting Redis..."
    # Start Redis server in the background
    redis-server &
    echo "Redis started."
fi

# Activate your Python virtual environment if you have one




# Start Celery worker for your project
# The -A option is the name of your Celery instance (app.tasks.celery_app in this case)
# The --loglevel option specifies the logging level
# The -c option specifies the number of worker processes. Use 1 for strict ordering
celery -A app.tasks.celery_app worker --loglevel=info -c 1

# If you are using a Celery beat scheduler for periodic tasks, you can also start it with:
# celery -A app.tasks.celery_app beat --loglevel=info