""" Logs config for client """
from loguru import logger
import os
import sys
sys.path.append('../')
from PyChat.common.variables import LOGGING_LEVEL
from PyChat.logs.common_config_log import make_filter


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

client_log_file_path = os.path.join(BASE_DIR, 'client.log')

logger.remove(0)
logger.start(sys.stderr, level=LOGGING_LEVEL)
logger.add(client_log_file_path, rotation="50 MB", encoding='utf-8',
           level='WARNING', filter=make_filter("client_dist"))

if __name__ == '__main__':
    client_logger = logger.bind(name='client_dist')
    client_logger.critical('Test critical event')
    client_logger.error('Test error event')
    client_logger.warning('Test error event')
    client_logger.debug('Test debug event')
    client_logger.info('Test info event')
