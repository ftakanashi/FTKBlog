# -*- coding:utf-8 -*-

STANDARD_FORMATTER = {
    'format': '[%(asctime)s] %(filename)s [L.%(lineno)d] %(levelname)s  %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
}

STANDARD_ROTATE_HANDLER = {
    'level': 'DEBUG',
    'class': 'logging.handlers.RotatingFileHandler',
    'maxBytes': 1024 ** 2,
    'backupCount': 5,
    'formatter': 'standard'
}