""" IMPORTS """
import socket
from server_util import (
    initialise_rsa_cipher, get_public_key,
    extract_aes_key, extract_message,
    log_setup, log_message,
)


""" CONSTANTS """
SERVER_HOST = 'localhost'
SERVER_PORT = 4813
SERVER_ADDRESS = (SERVER_HOST, SERVER_PORT)
MAX_CLIENTS = 1


def handle_client() -> None:
    """ Handles a socket client """
    # Connect client
    client_socket, client_address = server.accept()
    print(f'[NEW CLIENT CONNECTION]: {client_address}')

    # Send base64-encoded public key
    print('===== Starting key exchange =====')
    public_key = get_public_key()
    client_socket.send(public_key)
    print('✔️ Sent RSA public key to client')

    # Get AES key from client
    aes_key = extract_aes_key(client_socket)
    print('✔️ Received AES key from client')
    print('===== Key exchange complete =====')

    # Setup client logs
    logs_dir = log_setup(client_socket, aes_key)

    # Listen for incoming data
    while True:
        message = extract_message(client_socket, aes_key)
        if not message:
            # End of stream
            break
        # print(message)
        log_message(message, logs_dir)

    # Disconnect client
    print(f'[CLIENT DISCONNECTED]: {client_address}')
    client_socket.close()



if __name__ == '__main__':
    # Set up RSA cipher
    initialise_rsa_cipher()

    # Start socket server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(SERVER_ADDRESS)
    server.listen(MAX_CLIENTS)
    print('🔈 Listening...')

    # Handle socket clients
    while True:
        handle_client()
