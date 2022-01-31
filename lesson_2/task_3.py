class PortNumber:
    def __init__(self, name):
        self.name = '_' + name

    def __get__(self, instance, instance_type):
        return getattr(instance, self.name, 7777)

    def __set__(self, instance, value):
        if not (value >= 0):
            raise ValueError("Port must be >= 0")
        setattr(instance, self.name, value)


class TestServer:

    port = PortNumber('local_port')
    port_2 = PortNumber('remote_port')

    def __init__(self):
        self.port = 100
        print(self.port)
        print(self.port_2)
        self.port_2 = -5


if __name__ == '__main__':
    server = TestServer()
