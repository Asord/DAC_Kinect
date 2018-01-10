import socket
from sys import getsizeof

from network import *

from getFilesInfo import getFilesInfo, serializedCompare

def check_files(data):
    print(str(data))

files = getFilesInfo("..")
files_info = files.getFilesInfo()

sock = socket.socket()
host = ''; port = 3567
doBind = True

while True:
    con = connect(sock, ('', 3567), True, doBind); if doBind: doBind = False
    res = recv(con, 8)

    if res == b'\x01':
        send(con, b'\x01')

        # receive files info size
        data = recv(con, 32); size = int.from_bytes(data, 'big')

        # receive files info
        data = recv(con, size)

        # compare files and get size of result
        result = serializedCompare(files_info, data)
        size = getsizeof(result).to_bytes(32, 'big')

        # send compare size and result
        send(con, size)
        send(con, result)


        send(con, b'\xff')

    elif res == -1:
        sock.close()
        break
