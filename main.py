import ssl
import socket
import subprocess
import threading
# sudo iptables -t nat -L PREROUTING -v -n --line-numbers
 # sudo iptables -t nat -D PREROUTING 1
def add_iptables_rule():
    rule = (
        "iptables -t nat -A PREROUTING -s 192.168.75.129 "
        "-d 140.113.0.0/16 -p tcp --dport 443 -j REDIRECT --to-ports 443"
    )

    try:
        subprocess.run(rule, shell=True, check=True)
        print("iptables rule added successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error adding iptables rule: {e}")

def remove_iptables_rule():
    rule = (
        "iptables -t nat -D PREROUTING -s 192.168.75.129 "
        "-d 140.113.0.0/16 -p tcp --dport 443 -j REDIRECT --to-ports 443"
    )

    try:
        subprocess.run(rule, shell=True, check=True)
        print("iptables rule removed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error removing iptables rule: {e}")



def start_ssl_server():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="certificates/host.crt", keyfile="certificates/host.key")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 443))
    s.listen(5)
    print("SSL server listening on port 443")

    while True:
        try:
            client_socket, addr = s.accept()
            ssl_socket = context.wrap_socket(client_socket, server_side=True)
            print(f"Accepted connection from {addr}")
            server_socket = create_ssl_connection()
            server_socket.settimeout(0.1)
            ssl_socket.settimeout(0.01)
            while True:
                try:
                    data1 = ssl_socket.recv(2048)
                    print('data1',data1.decode())
                    if data1: server_socket.send(data1)
                except socket.timeout:
                    print("data 1 Timeout occurred")
                    pass
                try:            
                    data2 = server_socket.recv(2048)
                    if data2: ssl_socket.send(data2)
                    print('data2',data2)
                    print(f"Data1: {len(data1)} bytes, data2: {len(data2)} bytes")
                    if not data1 and not data1: 
                        print("Closing connection")
                        break
                except socket.timeout:
                    print("data 2 Timeout occurred")
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
            
def create_ssl_connection():
    hostname = 'portal.nycu.edu.tw'
    port = 443
    context = ssl.create_default_context()
    sock = socket.create_connection((hostname, port))
    ssl_sock = context.wrap_socket(sock, server_hostname=hostname)
    print(f"SSL connection established with {hostname}")
    return ssl_sock


try:
    add_iptables_rule()
    start_ssl_server()
    
finally:
    remove_iptables_rule()