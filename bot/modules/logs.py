import logging
from ..constants import FORMAT

format = logging.Formatter(FORMAT)

def set_logging(for_, file, level = None):
    level = level or logging.INFO
    logger = logging.getLogger(for_)
    logger.setLevel(level)
    handler = logging.FileHandler(filename=file, encoding='utf-8', mode='w')
    handler.setFormatter(format)
    logger.addHandler(handler)
