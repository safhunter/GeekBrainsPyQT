import os
from subprocess import Popen, CREATE_NEW_CONSOLE, PIPE
import argparse


def main():
    data = input()
    first_client.communicate(data)
    out = last_client.stdout.read()
    print(out)


def client_chain_builder(path, name, chain_count: int) -> [Popen, Popen]:
    clients = []
    if chain_count > 0:
        stdin = PIPE
        client = None
        for i in range(chain_count):
            client = get_client(path, name, stdin, PIPE)
            if client:
                stdin = client.stdout
                clients.append(client)
        return [clients[0], clients[-1]]
    else:
        return [None, None]


def get_client(path, name, stdin, stdout):
    try:
        return Popen(['python', os.path.join(path, name)], creationflags=CREATE_NEW_CONSOLE,
                     stdin=stdin, stdout=stdout, universal_newlines=True)
    except Exception as ex:
        print(ex.args[0])
        return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process clients count.')
    parser.add_argument('--cc', type=int, default=2, help='Clients count')
    args = parser.parse_args()
    dir_path = os.path.dirname(__file__)
    if args.cc > 0:
        first_client, last_client = client_chain_builder(dir_path, 'client.py', args.cc)
        main()
    else:
        print(f'Wrong clients count: {args.cc}')
