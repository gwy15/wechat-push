import logging.config
import os
import json

configfile = os.environ.get('LOGGING_CONFIG', 'logging.json')
if os.path.exists(configfile):
    with open(configfile) as f:
        config = json.load(f)
    logging.config.dictConfig(config)
