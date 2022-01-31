import ipaddress
from task_1 import host_ping


def host_range_ping(subnet, start_host: int, end_host: int, prettify=False, **kwargs):
    try:
        ip_net = ipaddress.ip_network(subnet)
        hosts_list = list(ip_net.hosts())
        if (0 < start_host <= len(hosts_list)) and (0 < end_host <= len(hosts_list)) and \
                (start_host <= end_host):
            host_ping(hosts_list[start_host-1:end_host], prettify=prettify, **kwargs)
        else:
            print(f'Incorrect hosts range')
    except ValueError:
        print(f'Incorrect subnet')


if __name__ == '__main__':
    host_range_ping('192.168.181.0/24', 155, 156)
    # host_range_ping('192.168.181.15/24', 150, 152)
    # host_range_ping('192.168.181.0/24', 153, 152)
