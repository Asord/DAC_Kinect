import socket
from sys import getsizeof

from network import *
from getFilesInfo import getFilesInfo

files_info = getFilesInfo(".").getFormatedFileInfo()
files_info_size = getsizeof(files_info).to_bytes(32, 'big')

sock = socket.socket()
host = '192.168.1.40'; port = 3567

connect(sock, (host, port), False)

send(sock, b'\x01')

while True:
    result = recv(sock, 8)

    if result == b'\x01':

        # send files info size and file info
        send(sock, files_info_size)
        send(sock, files_info)

        # receive result size
        res = recv(sock, 32)
        size = int.from_bytes(res, 'big')

        # receive result and print it ##tmp
        data = recv(sock, size)
        print(data)

    elif result == b'\xff':
        sock.close()
        break