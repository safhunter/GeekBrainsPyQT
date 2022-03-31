""" Decorators """
import sys
from loguru import logger as loguru_logger


logger = loguru_logger.bind(name='server_dist') if sys.argv[0].find('client_dist') == -1 \
    else loguru_logger.bind(name='client_dist')


def log(func_to_log):
    """ Debug log decorator """
    def log_saver(*args, **kwargs):
        logger.debug(f'Call {func_to_log.__name__} with parameters {args} , {kwargs}. '
                     f'From module {func_to_log.__module__}')
        ret = func_to_log(*args, **kwargs)
        return ret
    return log_saver
