# -*- encoding: utf-8 -*-

import logging
import logging.config

LOGGING_CONFIG = {
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        'ml_jobcontrol.worker': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG'
    },
    'version': 1
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)

activate_logging = setup_logging()
