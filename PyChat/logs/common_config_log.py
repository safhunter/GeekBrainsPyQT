""" Common utils for logs config """


def make_filter(name):
    """
    Make a filter for filter binded logger
    :param name:  Name of the logger used in a .bind()
    :return: bind_filter function that returns True if a record from logger with given name
    """

    def bind_filter(record):
        return record["extra"].get("name") == name

    return bind_filter
