""" PyQT homework lesson 1, task 1 """
import locale
import platform
from subprocess import Popen, PIPE
import concurrent.futures
import ipaddress
from tabulate import tabulate


ENCODING = locale.getpreferredencoding()

ipaddress_list = [
    '8.8.4.4',
    '8.8.8.8',
    '172.16.10.54',
    '343.16.10.54',
    'fe80::481f:fd8a:ad3a:b574',
    '2001:4860:4860::8888',
    '::1',
    'yandex.ru',
    'fafagaa',
    12314,
    2130706433,
]


def address_ping(host) -> bool:
    """
    Ping the given host using sys command ping
    :param
        host: Hostname as an ip address or as a domain name
    :return:
        Returns True if host is reachable, False if not
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    if isinstance(host, str):
        host_address_str = host
    else:
        try:
            host_address_str = str(ipaddress.ip_address(host))
        except (ValueError, TypeError):
            print(f'Invalid host name: {host}')
            return False

    args = ['ping', param, '4', host_address_str]
    with Popen(args, stdout=PIPE, stderr=PIPE) as reply:
        code = reply.wait()

    return code == 0


def host_ping(hosts_list, prettify=False, **kwargs):
    """
    Ping a list of hosts and print results to console
    :param hosts_list: List of target hosts
    :param prettify: If True the 'tabulate' module is used to output to the console
    :param kwargs: Other parameters for 'tabulate' module
    """
    result_hosts = {
        'Reachable': [],
        'Unreachable': [],
    }

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(hosts_list)) as executor:
        futures = [executor.submit(address_ping, host) for host in hosts_list]
    for i, future in enumerate(futures):
        if future.result():
            result_hosts['Reachable'].append(str(hosts_list[i]))
        else:
            result_hosts['Unreachable'].append(str(hosts_list[i]))
    if prettify:
        print(tabulate(result_hosts, headers='keys', **kwargs))
    else:
        print(f'Reachable:\n{result_hosts["Reachable"]}\nUnreachable:\n{result_hosts["Unreachable"]}')


if __name__ == '__main__':
    host_ping(ipaddress_list)
