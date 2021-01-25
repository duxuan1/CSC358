import sys, os, time, socket, select


def parse_data(d: bytes):
    """

    """
    d = str(d).split("\\r\\n")
    req = d[0][2:].split(" ")
    method, url, version = req
    host = url[1:]
    return method, url, version, host


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
            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(2048)
                print('received {!r}'.format(data))
                if data:
                    # create a new client socket
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    method, url, version, host = parse_data(data)
                    request = bytes(method + " / " + version + " " + "\r\nHost: " + host + "\r\n\r\n", "utf-8")
                    # connects to the destination web server
                    client.connect((host, 80))
                    # forward the HTTP request
                    client.send(request)
                    # receive an HTTP response
                    response = client.recv(2048)
                    # forward this response back to the browser client
                    connection.send(response)
                else:
                    print('no data from', client_address)
                    break

        except:
            print("you receive your website")

        finally:
            # Clean up the connection
            connection.close()