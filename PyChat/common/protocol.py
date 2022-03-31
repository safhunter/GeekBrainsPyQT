from abc import ABC, abstractmethod
from datetime import datetime
import json
import re
from loguru import logger as ll
from errors import IncorrectDataReceivedError, ReqFieldMissingError, FieldValueError
from common.variables import *

logger = ll.bind(name='protocol_dist')


def get_message(data: (bytes, dict)):
    try:
        if isinstance(data, bytes):
            json_data = data.decode(ENCODING)
            msg_dict = json.loads(json_data)
            if not isinstance(msg_dict, dict):
                raise IncorrectDataReceivedError
            if not JIMHandlerBase.is_valid_time(msg_dict['time']):
                raise IncorrectDataReceivedError
        else:
            msg_dict = data
        action = msg_dict['action']
        if msg_dict['time'] == '':
            msg_dict['time'] = JIMHandlerBase.get_now_time()
        logger.info(f'Accepted action: {action}')
        request = JIMRequest(**msg_dict)
        return ObjectHandler.handle(request, action)
    except json.JSONDecodeError as json_decode_error:
        raise IncorrectDataReceivedError from json_decode_error
    except (KeyError, ValueError) as key_value_error:
        raise ReqFieldMissingError('action or time') from key_value_error


def get_response(data: (bytes, dict)):
    try:
        if isinstance(data, bytes):
            json_data = data.decode(ENCODING)
            msg_dict = json.loads(json_data)
            if not isinstance(msg_dict, dict):
                raise IncorrectDataReceivedError
        else:
            msg_dict = data
        response = int(msg_dict.pop('response'))
        logger.info(f'Accepted response with code: {response}')
        return JIMResponseHandler(response, **msg_dict)
    except json.JSONDecodeError as json_decode_error:
        raise IncorrectDataReceivedError from json_decode_error
    except (KeyError, ValueError) as key_value_error:
        raise ReqFieldMissingError('response') from key_value_error


class JIMRequest:
    def __init__(self, **_others):
        self.request = _others

    def handle(self, handler):
        handler.start_object(**self.request)


class JIMHandlerBase(ABC):

    def __init__(self):
        self._message_data = {}

    @property
    def message_data(self):
        return self._message_data

    @message_data.setter
    def message_data(self, data: dict):
        self._message_data = data

    @staticmethod
    def get_now_time():
        return str(datetime.now().timestamp())

    @staticmethod
    def is_account_name_valid(username):
        if not isinstance(username, str):
            return False
        if len(username) <= 255:
            return re.fullmatch(r'\w*', username)
        return False

    @staticmethod
    def is_valid_time(timestamp: str):
        return bool(datetime.fromtimestamp(float(timestamp)))

    @logger.catch
    def to_json(self):
        try:
            return json.dumps(self.message_data)
        except json.JSONDecodeError as json_decode_error:
            raise ValueError("Can't dumps JIMHandler object to json") from json_decode_error

    def to_send(self):
        self.message_data['time'] = self.get_now_time()
        js_message = json.dumps(self.message_data)
        return js_message.encode(ENCODING)


class JIMRequestHandlerBase(JIMHandlerBase):

    def __init__(self):
        super().__init__()

    @logger.catch
    def start_object(self, request: dict):
        if not isinstance(request, dict):
            raise TypeError("Can't start object JIMRequestHandler. The request is not a dict")
        if 'action' not in request:
            raise ValueError("Can't start object JIMRequestHandler. The request does not have an 'action' field")
        self.message_data.update(request)

    @abstractmethod
    def is_valid(self):
        pass

    @abstractmethod
    def get_response(self):
        pass

    def __str__(self):
        return str(self.message_data)


class JIMRequestPresenceHandler(JIMRequestHandlerBase):
    default_object = {
        'action': '',
        'time': '',
        'type': '',
        'user': {
            'account_name': '',
            'status': '',
        },
    }

    def __init__(self):
        super().__init__()
        self.message_data = self.default_object.copy()

    def is_valid(self) -> bool:
        try:
            return (self.message_data['action'] == 'presence') and \
                   (self.is_valid_time(self.message_data['time'])) and \
                   (isinstance(self.message_data['type'], str)) and \
                   (self.is_account_name_valid(self.message_data['user']['account_name']))
        except (KeyError, ValueError, OverflowError, OSError):
            return False

    def get_response(self):
        response = {
            'action': 'probe',
            'time': self.get_now_time(),
        }
        result = JIMRequestProbeHandler()
        result.start_object(response)
        return result.to_send()


class JIMRequestProbeHandler(JIMRequestHandlerBase):
    default_object = {
        'action': '',
        'time': '',
    }

    def __init__(self):
        super().__init__()
        self.message_data = self.default_object.copy()

    def is_valid(self) -> bool:
        try:
            return (self.message_data['action'] == 'probe') and \
                   (self.is_valid_time(self.message_data['time']))
        except (KeyError, ValueError, OverflowError, OSError):
            return False

    def get_response(self):
        return None


class ObjectHandler:
    @staticmethod
    def handle(obj, action):
        handler = factory.get_handler(action)
        obj.handle(handler)
        return handler


class RequestHandlerFactory:

    def __init__(self):
        self._allowed_requests = {}

    def register_action(self, action, handler):
        self._allowed_requests[action] = handler

    def get_handler(self, action):
        handler = self._allowed_requests.get(action)
        if not handler:
            raise ValueError(f'Unknown request action: {action}')
        return handler()


factory = RequestHandlerFactory()
factory.register_action('presence', JIMRequestPresenceHandler)
factory.register_action('probe', JIMRequestProbeHandler)


class JIMResponseHandler(JIMHandlerBase):
    _allowed_responses = {
        # information messages
        100: 'basic notification ',
        101: 'important notification',
        # success
        200: 'OK',
        201: 'created',
        202: 'accepted',
        # client side errors
        400: 'wrong request/JSON-object',
        401: 'not authorized',
        402: 'incorrect login/password',
        403: '(forbidden) the user is blocked',
        404: '(not found) user / chat is missing on the server',
        409: '(conflict) a user with this name is already connected',
        410: '(gone) recipient exists but is not available (offline)',
        # server side errors
        500: 'server error',
    }

    @property
    def allowed_responses(self):
        return self._allowed_responses

    def __init__(self, code: int, **_others):
        super().__init__()
        self.data = {}
        if code in self.allowed_responses:
            self.data['response'] = code
            try:
                self.data['time'] = _others['time']
            except KeyError as key_error:
                raise ReqFieldMissingError('time') from key_error
            if code > 399:
                self.data['error'] = \
                    _others.get('error', default=f'{self.allowed_responses[code]}')
            else:
                self.data['alert'] = \
                    _others.get('alert', default=f'{self.allowed_responses[code]}')
        else:
            raise FieldValueError('response', str(code))
