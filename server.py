import socket
from server_util import initialise_listener, get_public_key, decrypt_data

""" CONSTANTS """
PUBLIC_KEY_LEN = 600 # b64 len of 450 for key len
REC_DATA_LEN = 344 # b64 len of 256 for encrypted data

SERVER = 'localhost'
PORT = 1234

# Setup keys
initialise_listener()
public_key = get_public_key()

# Start server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))
server.listen(5)

while True:
    # Connect client
    client_socket, client_address = server.accept()
    print(f'[NEW CONNECTION]: {client_address}')

    # Send public key
    client_socket.send(public_key)
    print(f'Sent {len(public_key)} bytes')

    # Listen for data
    while True:
        msg = client_socket.recv(REC_DATA_LEN)
        if msg:
            print(decrypt_data(msg))
        else:
            break

    # Disconnect client
    print(f'[DISCONNECTED]: {client_address}')
    client_socket.close()
