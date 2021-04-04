""" IMPORTS """
import socket
from server_util import (
    initialise_RSA_cipher, get_public_key, extract_aes_cipher,
    extract_message, decrypt_message, receive_message,
    log_setup, log_message,
)


""" CONSTANTS """
SERVER = 'localhost'
PORT = 4813

MAX_CLIENTS = 1


def handle_client() -> None:
    """ Handles a socket client """
    # Connect client
    client_socket, client_address = server.accept()
    print(f'[NEW CONNECTION]: {client_address}')

    # Send public key
    public_key = get_public_key()
    client_socket.send(public_key)

    # Generate AES cipher with same settings as client
    aes_cipher = extract_aes_cipher(client_socket)

    # Setup client logs
    logs_dir = log_setup(client_socket, aes_cipher)

    # Listen for incoming data
    while True:
        encrypted_message = receive_message(client_socket)
        if not encrypted_message:
            # End of stream
            break
        encoded_message = decrypt_message(encrypted_message, aes_cipher)
        message = extract_message(encoded_message)
        # print(message)
        log_message(message, logs_dir)

    # Disconnect client
    print(f'[DISCONNECTED]: {client_address}')
    client_socket.close()



if __name__ == '__main__':
    # Set up RSA cipher
    initialise_RSA_cipher()

    # Start socket server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER, PORT))
    server.listen(MAX_CLIENTS)
    print('🔈 Listening...')

    # Handle socket clients
    while True:
        handle_client()
