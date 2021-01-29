import sys
import os
import time
import socket
import select


def init_server_sock():
    """
    initialize a non blocking server socket
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind(('localhost', 8888))
    server.listen(5)
    return server


def extra_info_from_data(data):
    """
    extract corresponding data we need to use from the original request
    sent by localhost
    """
    data = data.decode('utf-8').split('\r\n')
    request = data[0]
    file_name = request.replace("/", " ")
    request_data, host_name = extract_url(request.split(' ')[1])
    remain_request = bytes('\r\n'.join(data[2:]), 'utf-8')
    return request, file_name, request_data, host_name, remain_request


def extract_url(url):
    """
    extract the host name and the request data from url
    """
    print(url)
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
    return url[index:] + ' ', url[1:index]


def change_accept_encoding(request):
    """
    change the default http attribute Accept-Encoding from gzip to identity
    """
    request = request.decode('utf-8').split('\r\n')
    for i in range(len(request)):
        if request[i].startswith('Accept-Encoding'):
            request[i] = 'Accept-Encoding: identity'
    request = bytes('\r\n'.join(request), 'utf-8')
    return request


def update_response(response, s):
    """
    add the notification box, insert HTML code into somewhere in the 
    <body> region of the HTTP response.
    """
    text = '<p style="z-index:9999; position:fixed; top:20px; left:20px; width:200px;height:100px; ' \
           'background-color:yellow; padding:10px; font-weight:bold;">{} {}</p>'
    text = text.format(s, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    response = response.decode('utf-8', 'ignore').split('\r\n')  # list
    for i in range(len(response)):  # modify content-length
        if response[i].startswith('Content-Length'):
            length = int(response[i][16:]) + len(text)
            response[i] = 'Content-Length: {}'.format(str(length))
            break
    html_code = response[-1]
    html_code = html_code.split('\n')
    for i in range(len(html_code)):    # modify html code, add notification box inside <body></body>
        if html_code[i] == '</body>':
            html_code.insert(i, text)
            break
    if i == len(html_code) - 1:   # bad html code without </body> tag, add notification box in the front of the doc
        html_code.insert(0, text)
    html_code = '\n'.join(html_code)
    response[-1] = html_code
    response = '\r\n'.join(response)
    response = bytes(response, 'utf-8')
    return response


def main():
    """
    main program of running socket server
    """
    server = init_server_sock()
    inputs = [server]
    outputs = []
    expire_time = float(sys.argv[1])
    while True:
        # use select to select socket that has data
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        for s in readable:
            if s is server:  # if it's server socket then accept connection
                connection, client_address = s.accept()
                connection.setblocking(0)
                inputs.append(connection)
            else:
                data = s.recv(1024)
                if data:
                    request, file_name, request_data, host_name, remain_request = extra_info_from_data(data)
                    if os.path.isfile(file_name) and \
                            float(os.path.getmtime(file_name)) + expire_time >= float(time.time()):
                        f = open(file_name, "rb")
                        s.send(f.read())
                        f.close()
                    else:
                        try:
                            web_ser_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            web_ser_socket.connect((host_name, 80))
                            request = bytes('GET' + ' ' + request_data + 'HTTP/1.1' + '\r\nHost: '
                                            + host_name + '\r\n', "utf-8") + remain_request
                            request = change_accept_encoding(request)  # change default accept encoding to identity
                            web_ser_socket.send(request)
                            response = cache_data = web_ser_socket.recv(10000000)
                            if bytes('Referer: ', 'utf-8') not in request:  # step5 modify html code
                                response = update_response(response, 'FRESH VERSION AT:')
                                cache_data = update_response(response, 'CACHED VERSION AS OF:')
                            f = open(file_name, "wb")
                            f.write(cache_data)
                            s.send(response)
                            web_ser_socket.close()
                            f.close()

                        except IOError:
                            print(host_name)
                else:
                    inputs.remove(s)


if __name__ == "__main__":   # main program
    main()

