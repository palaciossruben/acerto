import os
import json
import paramiko
import atexit

prefix_command = None
cd_path = None


def get_current_path():
    return os.path.dirname(os.path.abspath(__file__))


def run(command):

    global c

    if prefix_command:
        command = '{prefix} {command}'.format(prefix=prefix_command, command=command)

    if cd_path:
        command = 'cd {cd_path}; {command}'.format(cd_path=cd_path,
                                                   command=command)

    #commands = ["cd acerto && ls", "ls"]

    #for command in commands:
    print("run: {}".format(command))
    stdin, stdout, stderr = c.exec_command(command)
    out = stdout.read()
    print(out)
    print("Errors")
    print(stderr.read())

    return str(out)


class env:
    cwd = 'sa'


class cd:

    def __init__(self, path):
        global cd_path
        cd_path = path

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(exc_type, exc_value, traceback)

    def __enter__(self):
        pass


class prefix:

    def __init__(self, command):
        global prefix_command
        prefix_command = command

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(exc_type, exc_value, traceback)

    def __enter__(self):
        pass


def exit_handler():
    global c
    c.close()


json_data = open(os.path.join(get_current_path(), 'deploy_credentials.json'), encoding='utf-8').read()
credentials = json.loads(json_data)

k = paramiko.RSAKey.from_private_key_file(credentials['key'])
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print("connecting")
c.connect(hostname=credentials['host'], username=credentials['user'], pkey=k)
print("connected")
atexit.register(exit_handler)
