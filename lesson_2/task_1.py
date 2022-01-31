import socket
import dis


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
                        print(f'WARNING: Forbidden call socket.{instr.argrepr}() in {name}.{value.__name__}(), '
                              f'line: {line}')
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
            print(f'Class {cls.__name__} doesnt use module socket')
        else:
            for key, value in cls.__dict__.items():
                if hasattr(value, "__call__"):
                    bytecode = dis.Bytecode(value)
                    line = None
                    func_attr = None
                    for instr in bytecode:
                        if instr.opname == 'LOAD_ATTR':
                            func_attr = instr.argrepr
                        if instr.starts_line:
                            line = instr.starts_line
                        if func_attr in socket_objects and \
                                instr.opname == 'LOAD_METHOD' and \
                                instr.argrepr in cls.forbidden_calls:
                            print(f'WARNING: Forbidden call socket.{instr.argrepr}() in '
                                  f'{cls.__name__}.{value.__name__}(), line: {line}')
        return _instance


class TestClient(metaclass=ClientVerifier):
    def __init__(self):
        self.s = socket.socket()


class TestClient2(metaclass=ClientVerifier):
    def __init__(self):
        self.s = 1


class TestClient3(metaclass=ClientVerifier):
    def __init__(self, s):
        self._s = s

    def listen(self):
        self._s.listen(1)


if __name__ == '__main__':
    sock = socket.socket()
    sock.bind(('', 7777))
    client3 = TestClient3(sock)
    client2 = TestClient2()
    client = TestClient()

