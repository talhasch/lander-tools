import logging
import os
import tempfile
from logging.handlers import RotatingFileHandler

log_path = os.path.join(tempfile.gettempdir(), '')


def create_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # file logger
    handler_file = RotatingFileHandler('lander.log', maxBytes=1024 * 100000, backupCount=10)
    handler_file.setFormatter(formatter)
    logger.addHandler(handler_file)

    # screen logger
    handler_screen = logging.StreamHandler()
    handler_screen.setFormatter(formatter)
    logger.addHandler(handler_screen)

    return logger
