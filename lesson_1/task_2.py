""" PyQT homework lesson 1, task 2 """
import ipaddress
from task_1 import host_ping


def host_range_ping(start_host, hosts_count: int, prettify=False, **kwargs):
    """
    Ping a range of the ip addresses from the start_host with the step equal 1.
    Only the last octet changes in the address
    :param start_host: IP address of the start host
    :param hosts_count: Count of hosts to ping. If count > 0 addresses will increase, if < 0 will decrease
    :param prettify: If True the 'tabulate' module is used to output to the console
    :param kwargs: Other parameters for 'tabulate' module
    :return: None
    """
    if hosts_count > 0:
        count = hosts_count
    elif hosts_count < 0:
        count = -1 * hosts_count
    else:
        print('Incorrect hosts count')
        return
    count = min(count, 255)

    try:
        start_address = ipaddress.ip_address(start_host)
        octets = str(start_address).split(".")
        last_octet = int(octets[3])
        if hosts_count > 0:
            first_range = min(count, 256 - last_octet)
            second_range = max(0, last_octet + count - 256)
            octets[3] = '1'
            target_list = [start_address + i for i in range(first_range)] + \
                          [ipaddress.ip_address('.'.join(octets)) + i for i in range(second_range)]
        else:
            first_range = min(count, last_octet)
            second_range = max(0, count - last_octet)
            octets[3] = '255'
            target_list = [start_address - i for i in range(first_range)] + \
                          [ipaddress.ip_address('.'.join(octets)) - i for i in range(second_range)]
    except ValueError:
        print('Incorrect start address')
        return

    host_ping(target_list, prettify=prettify, **kwargs)


if __name__ == '__main__':
    host_range_ping('127.0.0.250', 20)
    # host_range_ping('192.168.181.15/24', 150, 152)
    # host_range_ping('192.168.181.0/24', 153, 152)
