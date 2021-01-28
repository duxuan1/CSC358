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

    while True:
        # Wait for a connection
        print('waiting for a connection')
        connection, client_address = sock_server.accept()
        try:
            print('connection from', client_address)
            data = connection.recv(100000)
            if not data:
                break
            web_ser_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            request, host_name = get_host_and_request(data)
            web_ser_socket.connect((host_name, 80))
            web_ser_socket.send(request)

            response = bytes("HTTP/1.1 200 OK\r\n\r\n", "utf-8")
            while response:
                connection.sendall(response)
                response = web_ser_socket.recv(100000)

        except:
            print("you receive your website")

        finally:
            # Clean up the connection
            connection.close()
