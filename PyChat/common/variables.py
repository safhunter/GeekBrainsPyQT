""" Contains common config variables """
import os
from dotenv import dotenv_values

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

shared_config = {
    **dotenv_values(os.path.join(BASE_DIR, '.env.shared')),
}
# Порт поумолчанию для сетевого ваимодействия
DEFAULT_PORT = int(shared_config['DEFAULT_PORT'])
# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = shared_config['DEFAULT_IP_ADDRESS']
# Максимальная очередь подключений
MAX_CONNECTIONS = int(shared_config['MAX_CONNECTIONS'])
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = int(shared_config['MAX_PACKAGE_LENGTH'])
# Кодировка проекта
ENCODING = shared_config['ENCODING']
# # Текущий уровень логирования
LOGGING_LEVEL = shared_config['LOGGING_LEVEL']

# Прококол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'

# Словари - ответы:
# 200
RESPONSE_200 = {RESPONSE: 200}
# 400
RESPONSE_400 = {
            RESPONSE: 400,
            ERROR: None
        }

if __name__ == '__main__':
    print(shared_config)
    print(DEFAULT_PORT)
    print(type(DEFAULT_PORT))
