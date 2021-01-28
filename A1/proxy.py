import sys, os, time, socket, select


def extract(url):
    count = 0
    index = 0
    for i in range(len(url)):
        if url[i] == '/':
            count += 1
        if count == 2:
            index = i
            break
    if count != 2:
        return '/ ', url[1:]
    return url[index:] + '\r\n', url[1:index]


def get_host_and_request(data):
    request = str(data).split('\\r\\n')[0]
    lst = request[2:].split(" ")
    http_method = lst[0]
    url = lst[1]
    http_protocol = lst[2]
    data, host_name = extract(url)
    request = bytes(http_method + ' ' + data + http_protocol + "\r\nHost: " +
                    host_name + "\r\n\r\n", "utf-8")
    return request, host_name


if __name__ == "__main__":
    # Create a TCP/IP socket
    sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('localhost', 8888)
    print('starting up on {} port {}'.format(*server_address))
    sock_server.bind(server_address)

    # Listen for incoming connections
    sock_server.listen(1)

    read_lst, write_lst, exceptions_lst = [sock_server], [], []

    while True:
        read, write, exceptions = select.select(read_lst, write_lst, exceptions_lst)
        for s in read:
            if s is sock_server:
                # Wait for a connection
                print('waiting for a connection')
                connection, client_address = s.accept()
                try:
                    print('connection from', client_address)
                    data = connection.recv(100000)
                    if not data:
                        break
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    request, host_name = get_host_and_request(data)
                    client.connect((host_name, 80))
                    client.send(request)

                    response = bytes("HTTP/1.1 200 OK\r\n\r\n", "utf-8")
                    while response:
                        connection.sendall(response)
                        response = client.recv(100000)
                    client.close()

                except IOError:
                    exit(1)

                finally:
                    # Clean up the connection
                    connection.close()

            else:
                by = s.recv(100000)
                if not bytes:
                    s.close()
                    read_lst.remove(s)


