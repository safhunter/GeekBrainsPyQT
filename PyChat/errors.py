""" Custom exceptions module """


class IncorrectDataReceivedError(Exception):
    """ Exception - wrong data from socket """

    def __str__(self):
        return 'Incorrect message received from remote host'


class ServerError(Exception):
    """ Exception - server error """
    def __init__(self, text):
        # super().__init__()
        self.text = text

    def __str__(self):
        return self.text


class NonDictInputError(Exception):
    """ Exception - argument must be a dict """
    def __str__(self):
        return 'Function argument must be a dict'


class ReqFieldMissingError(Exception):
    """ Exception - Missing required field  """
    def __init__(self, missing_field):
        # super().__init__()
        self.missing_field = missing_field

    def __str__(self):
        return f'Missing required field {self.missing_field} in incoming dict.'


class FieldValueError(Exception):
    """ Exception -  Message field has wrong value  """
    def __init__(self, field='Unknown', value='Unknown'):
        # super().__init__()
        self.field = field
        self.value = value

    def __str__(self):
        return f"Message field '{self.field}' contains a wrong value: '{self.value}'."
