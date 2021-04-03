""" IMPORTS """
import socket
from server_util import FORMAT, initialise_cipher, get_public_key, decrypt_data

""" CONSTANTS """
SERVER = 'localhost'
PORT = 1234
MAX_CONNECTIONS = 5

PUBLIC_KEY_LEN = 600 # b64 len of 450 for key len
CLIENT_DATA_LEN = 256


def receive_message(client_socket) -> str:
    """ Receives a message from a client socket """
    # receive number of blocks
    num_blocks = client_socket.recv(CLIENT_DATA_LEN).decode(FORMAT)
    if not num_blocks:
        return ''

    num_blocks = int(num_blocks)
    print(f'Receiving {num_blocks} blocks')

    # receive rest of message in blocks
    message = ''
    for _ in range(num_blocks):
        # receive and decrypt each block
        encrypted_block = client_socket.recv(CLIENT_DATA_LEN)
        decrypted_block = decrypt_data(encrypted_block)
        message += decrypted_block

    return message


def handle_client() -> None:
    """ Handles a socket client """
    # connect client
    client_socket, client_address = server.accept()
    print(f'[NEW CONNECTION]: {client_address}')

    # send public key
    client_socket.send(public_key)

    # listen for incoming data
    while True:
        message = receive_message(client_socket)
        if not message:
            break
        print(message)

    # disconnect client
    print(f'[DISCONNECTED]: {client_address}')
    client_socket.close()



if __name__ == '__main__':
    # set up RSA keys and cipher
    initialise_cipher()
    public_key = get_public_key()

    # start server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER, PORT))
    server.listen(MAX_CONNECTIONS)
    print('🔈 Listening...')

    while True:
        handle_client()
