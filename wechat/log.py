import logging

logger = logging.getLogger('wechat')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
