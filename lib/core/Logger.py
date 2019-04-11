#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import colorlog

DEBUG   = '[D]'
INFO    = '[*]'
SUCCESS = '[+]'
WARNING = '[X]'
ERROR   = '[!]'

LOG_FORMAT   = '%(log_color)s%(levelname)s%(reset)s %(message_log_color)s%(message)s'
DATE_FORMAT  = '%H:%M:%S'

LOG_COLORS = {
    DEBUG    : 'bold,white',
    INFO     : 'bold,blue',
    SUCCESS  : 'bold,green',
    WARNING  : 'bold,yellow',
    ERROR    : 'bold,red',
}

SECONDARY_LOG_COLORS = {
        'message': {
            DEBUG    : 'white',
            SUCCESS  : 'green',
            WARNING  : 'yellow',
            ERROR    : 'red',
        }
}

handler   = colorlog.StreamHandler()

formatter = colorlog.ColoredFormatter(LOG_FORMAT,
                                      datefmt=DATE_FORMAT,
                                      reset=True,
                                      log_colors=LOG_COLORS,
                                      secondary_log_colors=SECONDARY_LOG_COLORS,
                                      style='%')
handler.setFormatter(formatter)
logger = colorlog.getLogger()

logging.SUCCESS = 35
logging.addLevelName(logging.DEBUG, DEBUG)
logging.addLevelName(logging.INFO, INFO)
logging.addLevelName(logging.SUCCESS, SUCCESS)
logging.addLevelName(logging.WARNING, WARNING)
logging.addLevelName(logging.ERROR, ERROR)
setattr(logger, 'success', 
    lambda message, *args: logger._log(logging.SUCCESS, message, args))

logger.setLevel('INFO')
logger.addHandler(handler)

logging.getLogger('urllib3').setLevel(logging.CRITICAL)
