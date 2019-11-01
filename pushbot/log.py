import logging

logger = logging.getLogger('pushbot')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
