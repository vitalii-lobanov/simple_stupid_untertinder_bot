import logging
import colorlog

# Create a logger
d_logger = logging.getLogger('my_logger')
d_logger.setLevel(level="DEBUG")  # Set the logging level

colored_formatter = colorlog.ColoredFormatter(
    "%(module)s.%(funcName)s ||| %(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s "
    "%(white)s%(bg_blue)s%(asctime)s ",
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

# Create a console handler and set the formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(colored_formatter)

# Add the handler to the logger
d_logger.addHandler(console_handler)