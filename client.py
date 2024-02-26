import socket
import subprocess
import shlex


SERVER = 'localhost'
DATA_PORT = 8020 
CTRL_PORT = 8021
BUFFER_SIZE = 1024


def send(request):
    try:
        control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        control_socket.settimeout(2)
        control_socket.connect((SERVER, CTRL_PORT))
        control_socket.sendall(request.encode())
        response = control_socket.recv(1024).decode()
        control_socket.close()

    except:
        response = 'Server is Offline'

    return response
    

def main():
    request = 'HELP'
    response = send(request)
    print(response)

    while True:
        request = input().strip()
        response = send(request)
        if response == 'Server is Offline':
            print(response)
            break

        if response == 'Ready Retr':
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.settimeout(2)
            data_socket.connect((SERVER, DATA_PORT))

            file_name = './downloads/' + request.split()[1].split('/')[-1]
            command = 'mkdir -p ./downloads/' 
            subprocess.run(shlex.split(command), stdout=subprocess.PIPE).stdout.decode()
            command = 'rm -rf ' + file_name
            subprocess.run(shlex.split(command), stdout=subprocess.PIPE).stdout.decode()
            command = 'touch ' + file_name
            subprocess.run(shlex.split(command), stdout=subprocess.PIPE).stdout.decode()
            try:
                with open(file_name, 'ab') as f:
                    while True:
                        data = data_socket.recv(BUFFER_SIZE)
                        if not data:
                            break
                        f.write(data)

                data_socket.close()

                control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                control_socket.settimeout(2)
                control_socket.connect((SERVER, CTRL_PORT))
                response = control_socket.recv(1024).decode()
                control_socket.close()

            except:
                response = '400 Connection loss\n'


        elif response == 'Ready Stor':
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.settimeout(2)
            data_socket.connect((SERVER, DATA_PORT))

            file_name = request.split()[1]
            try:
                with open(file_name, 'rb') as f:
                    data = f.read(BUFFER_SIZE)
                    while data:
                        data_socket.sendall(data)
                        data = f.read(BUFFER_SIZE)

                data_socket.close()

                control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                control_socket.settimeout(2)
                control_socket.connect((SERVER, CTRL_PORT))
                response = control_socket.recv(1024).decode()
                control_socket.close()

            except:
                response = '400 Connection loss\n'


        elif response == 'Not Ready':
                control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                control_socket.settimeout(2)
                control_socket.connect((SERVER, CTRL_PORT))
                response = control_socket.recv(1024).decode()
                control_socket.close()

        elif response == '200 Goodnight!':
            print(response)
            break
        
        print(response)
    

if __name__ == '__main__':
    main()
        
