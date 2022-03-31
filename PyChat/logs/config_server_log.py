""" Logs config for client """
from loguru import logger
import os
import sys
sys.path.append('../')
from common.variables import LOGGING_LEVEL
from logs.common_config_log import make_filter


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

server_log_file_path = os.path.join(BASE_DIR, 'server.log')

logger.remove(0)
logger.start(sys.stderr, level=LOGGING_LEVEL)
logger.add(server_log_file_path, rotation="1 day", encoding='utf-8',
           level='WARNING', filter=make_filter("server_dist"))

if __name__ == '__main__':
    client_logger = logger.bind(name='server_dist')
    client_logger.critical('Test critical event')
    client_logger.error('Test error event')
    client_logger.warning('Test error event')
    client_logger.debug('Test debug event')
    client_logger.info('Test info event')
