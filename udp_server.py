import socket

# Define server IP and port
server_ip = None
server_port = None
server_socket = None
client_address = None
connection_established = False

def init_udp_server(server_ip_input='127.0.0.1', server_port_input = 12345):
    # Define server IP and port
    global server_ip
    global server_port
    global server_socket

    server_ip = server_ip_input  # Use loopback IP address or 'localhost'
    server_port = server_port_input  # Choose a port number (can be any available port)

    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((server_ip, server_port))
    print(f"Server listening on {server_ip}:{server_port}")
    ping_client()

def ping_client():
    while True:
        print("Waiting for client to ping...")
        data, client = server_socket.recvfrom(1024)
        if data.decode() == "Ping":
            global connection_established
            global client_address
            connection_established = True
            client_address = client
            print(f"Received ping from {client_address}. Connection established.")
            return
    


def udp_server(response_data):
    if connection_established:

            # Send a response back to the client
            server_socket.sendto(response_data.encode('utf-8'), client_address)
