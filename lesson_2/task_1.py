import socket
import json
import dis
from loguru import logger
import threading


class ClientVerifier(type):
    forbidden_calls = ['socket', 'accept', 'listen']

    def __init__(cls, name, bases, attr_dict):
        use_socket = False
        for key, value in attr_dict.items():
            if hasattr(value, "__call__"):
                bytecode = dis.Bytecode(value)
                line = None
                for instr in bytecode:
                    if instr.starts_line:
                        line = instr.starts_line
                    if instr.opname == 'LOAD_GLOBAL' and instr.argrepr == 'socket':
                        use_socket = True
                    if use_socket and instr.opname == 'LOAD_METHOD' and instr.argrepr in cls.forbidden_calls:
                        logger.warning(f'WARNING: Forbidden call socket.{instr.argrepr}() in '
                                       f'{name}.{value.__name__}(), line: {line}')
        super().__init__(name, bases, attr_dict)

    def __call__(cls, *args, **kwargs):
        _instance = super().__call__(*args, **kwargs)
        socket_objects = []
        use_socket = False
        for key, value in _instance.__dict__.items():
            if isinstance(value, socket.socket):
                socket_objects.append(key)
                use_socket = True
        if not use_socket:
            logger.warning(f'Class {cls.__name__} doesnt use module socket')
        else:
            logger.debug(f'Class {cls.__name__} use module socket')
            for key, value in cls.__dict__.items():
                if hasattr(value, "__call__"):
                    bytecode = dis.Bytecode(value)
                    line = None
                    func_attr = None
                    for instr in bytecode:
                        if instr.opname in ('LOAD_ATTR', 'LOAD_FAST'):
                            func_attr = instr.argrepr
                        if instr.starts_line:
                            line = instr.starts_line
                        if func_attr in socket_objects and \
                                instr.opname == 'LOAD_METHOD' and \
                                instr.argrepr in cls.forbidden_calls:
                            logger.warning(f'WARNING: Forbidden call socket.{instr.argrepr}() in '
                                           f'{cls.__name__}.{value.__name__}(), line: {line}')
        return _instance


class TestClient(metaclass=ClientVerifier):
    def __init__(self):
        self._s = socket.socket()


class TestClient2(metaclass=ClientVerifier):
    def __init__(self):
        self._s = 1


class TestClient3(metaclass=ClientVerifier):
    def __init__(self, client_sock):
        self._s = client_sock

    def listen(self):
        self._s.listen(1)


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        sock.listen()
        super().__init__()

    # Функция создаёт словарь с сообщением о выходе.
    def create_exit_message(self):
        return {}

    # Функция запрашивает кому отправить сообщение и само сообщение, и отправляет полученные данные на сервер.
    def create_message(self):
        to = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {}
        logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            logger.info(f'Отправлено сообщение для пользователя {to}')
        except:
            logger.critical('Потеряно соединение с сервером.')
            exit(1)

    # Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения
    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    pass
                except:
                    pass
                print('Завершение соединения.')
                logger.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    # Функция выводящяя справку по использованию.
    def print_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')


# Класс-приёмник сообщений с сервера. Принимает сообщения, выводит в консоль.
class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    # Основной цикл приёмника сообщений, принимает сообщения, выводит в консоль. Завершается при потере соединения.
    def run(self):
        while True:
            try:
                print(f'\nПолучено сообщение от пользователя')
                logger.info(f'Получено сообщение от пользователя ')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                logger.critical(f'Потеряно соединение с сервером.')
                break


if __name__ == '__main__':
    sock = socket.socket()
    sock.bind(('', 7777))
    client = TestClient()
    client2 = TestClient2()
    client3 = TestClient3(sock)
    client4 = ClientSender('default', sock)
    client5 = ClientReader('default', sock)
