from loguru import logger


class PortNumber:

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name

    def __get__(self, instance, instance_type):
        return getattr(instance, self.private_name, 7777)

    def __set__(self, instance, value):
        logger.debug(f"Updating port {self.public_name} to {value}")
        if not (value >= 0):
            logger.error(f"Unable to update port {self.public_name} to {value}")
            raise ValueError("Port must be >= 0")
        setattr(instance, self.private_name, value)


class TestServer:

    local_port = PortNumber()
    remote_port = PortNumber()

    def __init__(self):
        self.local_port = 100
        print(self.local_port)
        print(self.remote_port)
        self.remote_port = -5


if __name__ == '__main__':
    server = TestServer()
