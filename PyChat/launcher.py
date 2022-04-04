""" Launch server and n clients  """
import os
import subprocess
import signal
import sys
from time import sleep

PYTHON_PATH = sys.executable
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_subprocess(file_with_args):
    """ Run script with the given filename and return it process handler """
    sleep(0.2)
    file_full_path = f"{PYTHON_PATH} {BASE_PATH}/{file_with_args}"
    if os.name == 'POSIX':
        args = ["gnome-terminal", "--disable-factory", "--", "bash", "-c", file_full_path]
        return subprocess.Popen(args, start_new_session=True)  # preexec_fn=os.setpgrp)

    if os.name == 'NT':
        args = [file_full_path]
        return subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)

    raise OSError('Unknown OS!!!')


def kill_subprocess(victim):
    """ Terminate subprocess """
    if os.name == 'POSIX':
        os.killpg(victim.pid, signal.SIGINT)

    if os.name == 'NT':
        victim.kill()

    raise OSError('Unknown OS!!!')


processes = []
while True:
    TEXT_FOR_INPUT = "Выберите действие: q - выход, " \
                     "s - запустить сервер и клиенты, x - закрыть все окна: "
    action = input(TEXT_FOR_INPUT)

    if action == 'q':
        break
    if action == 's':
        clients_count = int(input('Введите количество тестовых клиентов для запуска: '))

        processes.append(get_subprocess("server.py"))

        for i in range(clients_count):
            processes.append(get_subprocess(f"client.py -n test{i + 1}"))

    elif action == 'x':
        while processes:
            process = processes.pop()
            kill_subprocess(process)
