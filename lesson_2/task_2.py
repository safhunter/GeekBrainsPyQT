import socket
import select
import dis
from loguru import logger


class ServerVerifier(type):
    forbidden_calls = ['connect']

    def __init__(cls, name, bases, attr_dict):
        cls.use_socket = False
        cls.call_socket = False
        is_socket_method = False
        for key, value in attr_dict.items():
            if hasattr(value, "__call__"):
                bytecode = dis.Bytecode(value)
                line = None
                # print(bytecode)
                for instr in bytecode:
                    if instr.starts_line:
                        line = instr.starts_line
                    if is_socket_method and instr.opname == 'LOAD_METHOD' and instr.argrepr == 'socket':
                        cls.call_socket = True
                    if instr.opname == 'LOAD_GLOBAL' and instr.argrepr == 'socket':
                        cls.use_socket = True
                        is_socket_method = True
                    else:
                        is_socket_method = False
                    if is_socket_method and instr.opname == 'LOAD_METHOD' and instr.argrepr in cls.forbidden_calls:
                        logger.warning(f'WARNING: Forbidden call socket.{instr.argrepr}() '
                                       f'in {name}.{value.__name__}(), line: {line}')
        super().__init__(name, bases, attr_dict)

    def __call__(cls, *args, **kwargs):
        _instance = super().__call__(*args, **kwargs)
        socket_objects = []
        for key, value in _instance.__dict__.items():
            # print(f'{key}: {value}')
            if isinstance(value, socket.socket):
                socket_objects.append(key)
                cls.use_socket = True
        if not cls.use_socket:
            logger.warning(f'Class {cls.__name__} doesnt use module socket')
        else:
            logger.debug(f'Class {cls.__name__} use module socket')
            is_socket_method = False
            for key, value in cls.__dict__.items():
                if hasattr(value, "__call__"):
                    bytecode = dis.Bytecode(value)
                    line = None
                    func_attr = None
                    for instr in bytecode:
                        if is_socket_method and instr.opname == 'LOAD_METHOD' and instr.argrepr == 'socket':
                            cls.call_socket = True
                        if instr.opname == 'LOAD_GLOBAL' and instr.argrepr == 'socket':
                            cls.use_socket = True
                            is_socket_method = True
                        else:
                            is_socket_method = False
                        if instr.opname in ('LOAD_ATTR', 'LOAD_FAST'):
                            func_attr = instr.argrepr
                        if instr.starts_line:
                            line = instr.starts_line
                        if func_attr in socket_objects and \
                                instr.opname == 'LOAD_METHOD' and \
                                instr.argrepr in cls.forbidden_calls:
                            logger.warning(f'WARNING: Forbidden call socket.{instr.argrepr}() in '
                                           f'{cls.__name__}.{value.__name__}(), line: {line}')
        if not cls.call_socket:
            logger.warning(f'Class {cls.__name__} doesnt call socket.socket()')
        else:
            logger.debug(f'Class {cls.__name__} call socket.socket()')
        return _instance


class TestServer(metaclass=ServerVerifier):
    def __init__(self):
        self.s = socket.socket()


class TestServer2(metaclass=ServerVerifier):
    def __init__(self):
        self.s = 1


class TestServer3(metaclass=ServerVerifier):
    def __init__(self, s):
        self._s = s

    def connection(self):
        self._s.connect()


class Server(metaclass=ServerVerifier):
    def __init__(self, listen_address, listen_port):
        # Параметры подключения
        self.addr = listen_address
        self.port = listen_port
        self.sock = None

        # Список подключённых клиентов.
        self.clients = []

        # Список сообщений на отправку.
        self.messages = []

        # Словарь содержащий сопоставленные имена и соответствующие им сокеты.
        self.names = dict()

    def init_socket(self):
        logger.info(
            f'Запущен сервер, порт для подключений: {self.port}, '
            f'адрес с которого принимаются подключения: {self.addr}. '
            f'Если адрес не указан, принимаются соединения с любых адресов.')
        # Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        # Начинаем слушать сокет.
        self.sock = transport
        self.sock.listen()

    def main_loop(self):
        # Инициализация Сокета
        self.init_socket()

        # Основной цикл программы сервера
        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            # принимаем сообщения и если ошибка, исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        pass
                    except:
                        logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

            # Если есть сообщения, обрабатываем каждое.
            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except Exception as e:
                    logger.info(f'Связь с клиентом с именем '
                                f'{message[1]} была потеряна, '
                                f' ошибка {e}')
                    self.clients.remove(self.names[message[1]])
                    del self.names[message[1]]
            self.messages.clear()

    # Функция адресной отправки сообщения определённому клиенту.
    # Принимает словарь сообщение, список зарегистрированных
    # пользователей и слушающие сокеты. Ничего не возвращает.
    def process_message(self, message, listen_socks):
        if message in self.names and \
                self.names[message] in listen_socks:
            # send_message(self.names[message[DESTINATION]], message)
            logger.info(f'Отправлено сообщение пользователю {message} '
                        f'от пользователя {message}.')
        elif message in self.names \
                and self.names[message] not in listen_socks:
            raise ConnectionError
        else:
            logger.error(
                f'Пользователь {message} не зарегистрирован '
                f'на сервере, отправка сообщения невозможна.')

    # Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента,
    # проверяет корректность, отправляет словарь-ответ в случае необходимости.
    def process_client_message(self, message, client):
        logger.debug(f'Разбор сообщения от клиента : {message}')
        # Если это сообщение о присутствии, принимаем и отвечаем
        if 1 in message and message == 1 \
                and 1 in message and 1 in message:
            # Если такой пользователь ещё не зарегистрирован, регистрируем,
            # иначе отправляем ответ и завершаем соединение.
            if message[1][1] not in self.names.keys():
                self.names[message[1][1]] = client
                # send_message(client, RESPONSE_200)
            else:
                response = 1
                response[1] = 'Имя пользователя уже занято.'
                # send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif 1 in message \
                and message[1] == 1 \
                and 1 in message \
                and 1 in message \
                and 1 in message \
                and 1 in message:
            self.messages.append(message)
            return
        # Если клиент выходит
        elif 1 in message \
                and message[1] == 1 \
                and 1 in message:
            self.clients.remove(self.names[1])
            self.names[1].close()
            del self.names[1]
            return
        # Иначе отдаём Bad request
        else:
            response = 1
            response[1] = 'Запрос некорректен.'
            # send_message(client, response)
            return


if __name__ == '__main__':
    sock = socket.socket()
    sock.bind(('', 7777))
    server = TestServer()
    server2 = TestServer2()
    server3 = TestServer3(sock)
    server4 = Server('127.0.0.1', 7777)
