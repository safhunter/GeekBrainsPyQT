import dis
import socket
from loguru import logger


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
