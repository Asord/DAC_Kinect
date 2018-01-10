from time import sleep


def recv(sock, size):
    try:
        return sock.recv(size)
    except Exception as e:
        print(e)


def send(sock, data):
    try:
        sock.send(data)
    except Exception as e:
        print(e)


def connect(sock, connection, host=False, bind=False):
    if host:
        if bind:
            sock.bind(connection)
            sock.listen(5)

        con, _ = sock.accept()
        return con

    else:
        print("Connection à l'hôte distant...")
        while True:
            try:
                sock.connect(connection)
                print("Connection réussi")
                return 0
            except:
                sleep(2)
