from task_2 import host_range_ping


def host_range_ping_tab(subnet, start_host: int, end_host: int):
    host_range_ping(subnet, start_host, end_host, prettify=True, tablefmt='pipe', stralign='center')


if __name__ == '__main__':
    host_range_ping_tab('192.168.181.0/24', 155, 156)
    host_range_ping_tab('192.168.181.0/24', 1, 3)

