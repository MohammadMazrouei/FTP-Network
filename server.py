import socket
import subprocess
import shlex
import os


ADMIN = 1
ORDINARY = 2
BAD_REQUEST = '400 Bad Request\n'
BUFFER_SIZE = 1024

server_name = os.getlogin()
DEFAULT_DIR = f'/home/{server_name}//ftp'
LOG_DIR = f'/home/{server_name}/ftp/admin/report.log'
HELP_DIR = f'/home/{server_name}/ftp/admin/help.hlp'
PRIVATE_FILES_DIR = f'/home/{server_name}/ftp/admin/private_files.txt'

DATA_PORT = 8020 
CTRL_PORT = 8021 
HOST = 'localhost'

private_files = []
users = []
online_users = []

class User:
    def __init__(self):
        self.authorized = False
        self.current_dir = DEFAULT_DIR 

    def set_username(self, username):
        self.username = username

    def set_password(self, password):
        self.password = password

    def set_privilage(self, privilage):
        self.privilage = privilage

    def set_authorized(self, authorized):
        self.authorized = authorized

    def set_current_dir(self, directory):
        self.current_dir = directory

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_privilage(self):
        return self.privilage

    def get_authorized(self):
        return self.authorized

    def get_current_dir(self):
        return self.current_dir

    def add_user(self, username, password, privilage):
        self.set_username(username)
        self.set_password(password)
        self.set_privilage(privilage)
        users.append(self)

    def authenticate(self):
        for user in users:
            if self.username == user.username and self.password == user.password:
                self.set_privilage(user.privilage)
                online_users.append(self)
                self.set_authorized(True)
                break

    def quit(self):
        online_users.remove(self)
        self.set_username('')
        self.set_password('')
        self.set_authorized(False)
        self.set_current_dir = DEFAULT_DIR
    
    def __str__(self):
        return f'username: {self.username}\npassword: {self.password}\nprivilage: {self.privilage}\nauthorization: {self.authorized}\ndir: {self.current_dir}'


def add_fake_users():
    user = User()
    user.add_user('m', '1', ORDINARY)
    user = User()
    user.add_user('p', '1', ADMIN) 
    user = User()


def read_private_files():
    try:
        with open(PRIVATE_FILES_DIR, 'r') as f:
            for line in f:
                private_files.append(line.strip())
    except:
        print('Can\'t open private files')


def is_private(path):
    file_name = path.split('/')[-1]
    return file_name in private_files


def handle_user(request, user):
    request_parts = request.strip().split()
    try:
        username = request_parts[1]
    except:
        return BAD_REQUEST

    user.set_username(username)
    user.set_authorized(False)
    response = '200 Username Set\n'
    return response


def handle_pass(request, user):
    request_parts = request.strip().split()
    try:
        password = request_parts[1]
    except:
        return BAD_REQUEST

    user.set_password(password)
    user.authenticate()
    if user.get_authorized():
        response = '200 Login Successfull\n'
    else:
        response = '400 Login Failed\n'
    return response


def handle_list(request, directory, access):
    request_parts = request.strip().split()
    if len(request_parts) > 1: 
        path = request_parts[1]
    else:
        path = ''

    command = f'ls {path} -ltrh'
    response = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, cwd=directory).stdout.decode()
    if 'total' not in response:
        if is_private(path) and access != ADMIN:
            response = '400 Access Denied\n'
        else:
            command = f'cat {path}'
            response = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, cwd=directory).stdout.decode() + '\n'

    return response


def handle_retr(request, client_control, data_socket, directory, access):
    request_parts = request.strip().split()
    try:
        file_name = directory + '/' + request_parts[1] 
    except:
        response = BAD_REQUEST
        return response

    try:
        if is_private(file_name) and access != ADMIN:
            response = '400 Access Denied\n'
            ready = 'Not Ready'
            client_control.sendall(ready.encode())
            client_control.close()
            return response

        ready = 'Ready Retr'
        client_control.sendall(ready.encode())
        client_control.close()

        print(f'Server is listening on ftp://{HOST}: {DATA_PORT}')
        client_data, client_address = data_socket.accept()
        print(f'port {DATA_PORT} opened')

        with open(file_name, 'rb') as f:
            data = f.read(BUFFER_SIZE)
            while data:
                client_data.sendall(data)
                data = f.read(BUFFER_SIZE)

        client_data.close()
        response = '200 File Received\n'

    except:
        response = '400 Connection Loss\n'

    return response


def handle_stor(request, client_control, data_socket, directory, access):
    request_parts = request.strip().split()
    try:
        file_name = directory + '/' + request_parts[2] 
    except:
        response = BAD_REQUEST
        return response

    try:
        if is_private(file_name) and access != ADMIN:
            response = '400 Access Denied\n'
            ready = 'Not Ready'
            client_control.sendall(ready.encode())
            client_control.close()
            return response

        ready = 'Ready Stor'
        client_control.sendall(ready.encode())
        client_control.close()

        print(f'Server is listening on ftp://{HOST}: {DATA_PORT}')
        client_data, client_address = data_socket.accept()
        print(f'port {DATA_PORT} opened')

        command = 'rm -rf ' + file_name
        subprocess.run(shlex.split(command), stdout=subprocess.PIPE).stdout.decode()
        command = 'touch ' + file_name
        subprocess.run(shlex.split(command), stdout=subprocess.PIPE).stdout.decode()
        with open(file_name, 'ab') as f:
            while True:
                data = client_data.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)

        client_data.close()
        response = '200 File Sent\n'

    except:
        response = '400 Connection Loss\n'

    return response


def handle_mkd(request, directory, access):
    request_parts = request.strip().split()
    try:
        path = request_parts[1]
    except:
        return BAD_REQUEST

    try:
        if is_private(path) and access != ADMIN:
            response = '400 Access Denied\n'
        else:
            command = 'mkdir -p ' + path 
            response = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, cwd=directory).stdout.decode()
            response = f'200 Directory "{path}" Created' if not response else '400 ' + response
            response += '\n'
    except:
        response = BAD_REQUEST

    return response 


def handle_rmd(request, directory, access):  
    request_parts = request.strip().split()
    try:
        path = request_parts[1]
    except:
        return BAD_REQUEST

    try:
        if is_private(path) and access != ADMIN:
            response = '400 Access Denied\n'
        else:
            command = 'rmdir ' + path
            response = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, cwd=directory).stdout.decode()
            response = f'200 Directory "{path}" Removed' if not response else '400 ' + response
            response += '\n'
    except:
        response = BAD_REQUEST

    return response 


def handle_pwd(directory):
    command = 'pwd'
    response = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, cwd=directory).stdout.decode()
    return response 


def handle_cwd(request, user, directory):
    request_parts = request.strip().split()
    try:
        path = request_parts[1]
    except:
        return BAD_REQUEST
    
    if path[0] == '/':
        path = DEFAULT_DIR + path 
    else:
        path = directory + '/' + path

    try:
        os.chdir(path)
        path = os.getcwd()
        if 'ftp' not in path:
            response = BAD_REQUEST
        else:
            user.set_current_dir(path)
            response = f'200 You are in {path}\n' 
    except:
        response = '400 Directory Not Found\n'

    return response 


def handle_dele(request, directory, access):
    request_parts = request.strip().split()
    try:
        path = request_parts[1]
    except:
        return BAD_REQUEST

    try:
        if is_private(path) and access != ADMIN:
            response = '400 Access Denied\n'
        else:
            command = 'rm -rf ' + path 
            response = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, cwd=directory).stdout.decode()
            response = f'200 Directory/File "{path}" Deleted' if not response else '400 ' + response
            response += '\n'
    except:
        response = BAD_REQUEST

    return response 


def handle_cdup(user, directory):
    return handle_cwd('cd ..', user, directory)


def handle_quit(user):
    user.quit()
    response = '200 Goodnight!'
    return response 


def handle_report(access):
    if access == ADMIN:
        try:
            command = 'cat ' + LOG_DIR
            response = subprocess.run(shlex.split(command), stdout=subprocess.PIPE).stdout.decode() + '\n'
        except:
            response = '400 Can\'t open log file\n'
    else:
        response = '400 Access Denied\n'

    return response


def handle_help():
    with open(HELP_DIR, 'r') as f:
        response = f.read()
    return response


def main():
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.bind((HOST, CTRL_PORT))
    control_socket.listen(1)
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.bind((HOST, DATA_PORT))
    data_socket.listen(1)

    print(f'Server is listening on ftp://{HOST}: {CTRL_PORT}')

    add_fake_users()
    read_private_files();
    user = User()

    while True:
        client_control, client_address = control_socket.accept()
        client_host = socket.gethostbyaddr(client_address[0])[0]
        request = client_control.recv(BUFFER_SIZE).decode()
        
        if request.upper() == 'HELP':
            response = handle_help()

        elif 'USER' in request.upper():
            with open(LOG_DIR, 'a') as f:
                f.write(f'User: Unknown\nRequest: {request}\n')
            response = handle_user(request, user)

        elif 'PASS' in request.upper():
            with open(LOG_DIR, 'a') as f:
                f.write(f'User: Unknown\nRequest: {request}\n')
            response = handle_pass(request, user)

        elif user.get_authorized():
            with open(LOG_DIR, 'a') as f:
                f.write(f'User: {user.get_username()}\nRequest: {request}\n')
            access = user.get_privilage()
            current_dir = user.get_current_dir()

            if any(x in request.upper() for x in ['LIST', 'LS']):
                response = handle_list(request, current_dir, access)

            elif 'RETR' in request.upper():
                response = handle_retr(request, client_control, data_socket, current_dir, access)
                client_control, client_address = control_socket.accept()

            elif 'STOR' in request.upper():
                response = handle_stor(request, client_control, data_socket, current_dir, access)
                client_control, client_address = control_socket.accept()

            elif any(x in request.upper() for x in ['MKD', 'MKDIR']):
                response = handle_mkd(request, current_dir, access)

            elif any(x in request.upper() for x in ['RMD', 'RMDIR']):
                response = handle_rmd(request, current_dir, access)

            elif 'PWD' in request.upper():
                response = handle_pwd(current_dir)

            elif 'CDUP' in request.upper():
                response = handle_cdup(user, current_dir)

            elif any(x in request.upper() for x in ['CWD', 'CD']):
                response = handle_cwd(request, user, current_dir)

            elif any(x in request.upper()for x in ['DELE', 'RM']):
                response = handle_dele(request, current_dir, access)

            elif any(x in request.upper() for x in ['QUIT']):
                response = handle_quit(user)

            elif request.upper() == 'REPORT': 
                response = handle_report(access)

            else:
                response = BAD_REQUEST

        else:
            response = '400 Login First!\n'

        with open(LOG_DIR, 'a') as f:
            if request.upper() != 'REPORT':
                f.write(f'Response: {response}\n')
            f.write('--------------------------------\n')

        client_control.sendall(response.encode())
        client_control.close()


if __name__ == '__main__':
    main()
        
