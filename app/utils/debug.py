import logging
import os

# Get the log level from an environment variable or default to INFO if not set
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

# Configure the logging
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(module)s.%(funcName)s: %(message)s',
)

# Use getLogger to create a logger object
logger = logging.getLogger(__name__)

# Now you can use this logger object to log messages, including debug messages.
def debug_message(message):
    logger.debug(message)

