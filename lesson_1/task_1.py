import subprocess
import chardet
import ipaddress
import re
from tabulate import tabulate

ipaddress_list = [
    '8.8.4.4',
    '8.8.8.8',
    '172.16.10.54',
    '343.16.10.54',
    'fe80::481f:fd8a:ad3a:b574',
    'yandex.ru',
    'fafagaa',
    12314,
]


def address_ping(host: str) -> [bool, str]:
    try:
        args = ['ping', host]
        with subprocess.Popen(args, stdout=subprocess.PIPE) as subproc_ping:
            ping_result = subproc_ping.stdout.read()
            char_enc = chardet.detect(ping_result)['encoding']
            decoded_result = ping_result.decode(char_enc)
        has_valid_response = re.search(r'\w+[=<]\d+', decoded_result)
        if has_valid_response:
            return [True, f'Reachable']
        else:
            return [False, f'Unreachable']
    except (UnicodeEncodeError, SyntaxError):
        return [False, f'Other error']


def host_ping(hosts_list, prettify=False, **kwargs):
    result_hosts = {
        'Reachable': [],
        'Unreachable': [],
    }
    domain_regexp = re.compile(r'^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,6}$')
    for host in hosts_list:
        if isinstance(host, str) and domain_regexp.match(host):
            reachable, msg = address_ping(host)
        else:
            try:
                ip = ipaddress.ip_address(host)
                reachable, msg = address_ping(str(ip))
            except ValueError:
                reachable = False
                msg = 'Invalid host name'
                print(f'Invalid host name: {host}')
        if prettify:
            if msg not in result_hosts.keys():
                result_hosts[msg] = []
            result_hosts[msg].append(host)
        else:
            if reachable:
                result_hosts['Reachable'].append(host)
            else:
                result_hosts['Unreachable'].append(host)
    if prettify:
        print(tabulate(result_hosts, headers='keys', **kwargs))
    else:
        print(f'Reachable:\n{result_hosts["Reachable"]}\nUnreachable:\n{result_hosts["Unreachable"]}')


if __name__ == '__main__':
    host_ping(ipaddress_list)
