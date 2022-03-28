""" PyQT homework lesson 1, task 3 """
from task_2 import host_range_ping


def host_range_ping_tab(start_host, hosts_count: int):
    """
    Call 'host_range_ping' with prettify=True
    :param start_host: IP address of the start host
    :param hosts_count: Count of hosts to ping. If count > 0 addresses will increase, if < 0 will decrease
    :return: None
    """
    host_range_ping(start_host, hosts_count, prettify=True, tablefmt='pipe', stralign='center')


if __name__ == '__main__':
    host_range_ping_tab('8.8.8.4', 6)
