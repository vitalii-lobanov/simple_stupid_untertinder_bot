#!/bin/bash

# Get the directory of the script
SCRIPT_DIR=$(dirname "$0")

# Change to the script's directory
cd "$SCRIPT_DIR"

# Set environment variables
export TELEGRAM_API_KEY="******"
export PYTHONPATH="$(pwd)/app"
export LOG_LEVEL="DEBUG"
export FORWARD_DEBUG_MESSAGES_TO_USERS="TRUE"

# Get the full path to the current working directory
WORKING_DIR=$(pwd)

# Start the Python debugger with the current file
# Replace 'your_script.py' with the script you want to debug
python  "$WORKING_DIR/app/utils/recreate_db.py"
