# import logging
# import os

# # Get the log level from an environment variable or default to INFO if not set
# log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

# # Configure the logging
# logging.basicConfig(
#     level=log_level,
#     format='%(asctime)s - %(levelname)s - [%(name)s] %(module)s.%(funcName)s: %(message)s',
# )

# # Use getLogger to create a logger object
# logger = logging.getLogger(__name__)

# # Now you can use this logger object to log messages, including debug messages.
# def debug_message(message):
#     logger.debug(message)

#------------------------------------

# from logging import getLogger
# import logging
# import os

# class Logger(logging.Logger):
#     def __init__(self):
#         self.logging_level = os.getenv('LOG_LEVEL', 'INFO').upper()
#         self.format='%(asctime)s - %(levelname)s - [%(name)s] %(module)s.%(funcName)s: %(message)s'  
#         super().__init__(
#             name = __name__,
#             level = self.logging_level,             
#         )
#         pass

#     def critical(self, message):
#         super().critical(msg=message)



# logger = Logger()
# logger.critical(message = "This is a critical message")

#------------------------------------

#import colorlog

# # Create a logger object
#logger = colorlog.getLogger()

# # Set the log level
# logger.setLevel(colorlog.DEBUG)

# # Create a formatter with color codes
# formatter = colorlog.ColoredFormatter(
#     "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
#     datefmt=None,
#     reset=True,
#     log_colors={
#         'DEBUG':    'cyan',
#         'INFO':     'green',
#         'WARNING':  'yellow',
#         'ERROR':    'red',
#         'CRITICAL': 'red,bg_white',
#     },
#     secondary_log_colors={},
#     style='%'
# )

# # Create a stream handler
# stream_handler = colorlog.StreamHandler()
# stream_handler.setFormatter(formatter)

# # Add the handler to the logger
# logger.addHandler(stream_handler)

# # Example usage
# logger.debug("A debug message")
# logger.info("An info message")
# logger.warning("A warning message")
# logger.error("An error message")
# logger.critical("A critical message")


#------------------------------------

# import logging
# import colorlog

# class CustomColorLogger(logging.Logger):
#     def __init__(self, name, level=logging.NOTSET):
#         super().__init__(name, level)
# # %(asctime)s - %(levelname)s - [%(name)s] %(module)s.%(funcName)s: %(message)s
#         colored_formatter = colorlog.ColoredFormatter(
#             #"%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s %(blue)s%(asctime)s | %(module)s %(funcName)s",
#              "%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s "
#             "%(green)s%(asctime)s | %(module)s.%(funcName)s",
#             datefmt=None,
#             reset=True,
#             log_colors={
#                 'DEBUG': 'cyan',
#                 'INFO': 'green',
#                 'WARNING': 'yellow',
#                 'ERROR': 'red',
#                 'CRITICAL': 'red,bg_white',
#             },
#             secondary_log_colors={},
#             style='%'
#         )

#         stream_handler = logging.StreamHandler()
#         stream_handler.setFormatter(colored_formatter)
#         self.addHandler(stream_handler)

#     def debug(self, msg, *args, **kwargs):
#         # Custom implementation for debug
#         super().debug(msg, *args, **kwargs)

#     def info(self, msg, *args, **kwargs):
#         # Custom implementation for info
#         super().info(msg, *args, **kwargs)

#     def warning(self, msg, *args, **kwargs):
#         # Custom implementation for warning
#         super().warning(msg, *args, **kwargs)

#     def error(self, msg, *args, **kwargs):
#         # Custom implementation for error
#         super().error(msg, *args, **kwargs)

#     def critical(self, msg, *args, **kwargs):
#         # Custom implementation for critical
#         super().critical(msg, *args, **kwargs)

# def test_func():
#     logger.debug("This is a debug message")
#     logger.info("This is an info message")
#     logger.warning("This is a warning message")
#     logger.error("This is an error message")
#     logger.critical("This is a critical message")

# # Example usage
# logger = CustomColorLogger('custom_logger')

# test_func()

#------------------------------------

import logging
import colorlog

class CustomColorLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        colored_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)-90s "
            "%(white)s%(bg_blue)s%(asctime)s | %(module)s.%(funcName)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(colored_formatter)
        self.addHandler(stream_handler)

    def debug(self, msg, *args, **kwargs):
        # Custom additional handling for debug
        self._log(logging.DEBUG, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=2, **kwargs)

    def info(self, msg, *args, **kwargs):
        # Custom additional handling for info
        self._log(logging.INFO, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=2, **kwargs)

    def warning(self, msg, *args, **kwargs):
        # Custom additional handling for warning
        self._log(logging.WARNING, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=2, **kwargs)

    def error(self, msg, *args, **kwargs):
        # Custom additional handling for error
        self._log(logging.ERROR, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=2, **kwargs)

    def critical(self, msg, *args, **kwargs):
        # Custom additional handling for critical
        self._log(logging.CRITICAL, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=2, **kwargs)

# Example usage
logger = CustomColorLogger('custom_logger')

def example_function():
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

example_function()